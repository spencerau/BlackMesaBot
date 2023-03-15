import discord
import json
import asyncio
import requests
import ffmpeg
import re
import traceback
import youtube_dl
from bs4 import BeautifulSoup


# Open the JSON file and load its contents
with open('key.json') as f:
    data = json.load(f)

# Access the values associated with the keys
key = data['key']


queue = []
videoSites = ['youtube.com', 'youtu.be', 'bitchute.com', 'goyimtv.com']
censorList = []

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!play'):
        url = message.content.split()[1]
        # change to use any()
        if True:
            await message.channel.send('Adding video to queue...')
            queue.append(url)
            if not message.guild.voice_client or not message.guild.voice_client.is_connected():
                voice_channel = message.author.voice.channel
                await voice_channel.connect()
            if not message.guild.voice_client.is_playing():
                await play_video(message, message.guild)
        else:
            await message.channel.send('Invalid URL')

    elif message.content == '!pause':
        if message.guild.voice_client and message.guild.voice_client.is_playing():
            message.guild.voice_client.pause()
            await message.channel.send('Playback paused.')
        else:
            await message.channel.send('Nothing is playing at the moment.')

    elif message.content == '!skip':
        if message.guild.voice_client and message.guild.voice_client.is_playing():
            message.guild.voice_client.stop()
            await message.channel.send('Skipping to the next video.')
            await play_video(message.guild)
        else:
            await message.channel.send('Nothing is playing at the moment.')

    elif 'kashmir' in message.content.lower():
        await message.channel.send("The Kashmir region is rightful Pakistani clay and Allah will bless "
                                   "the Hindu Pagan invaders with holy nuclear hellfire, Inshallah.")


async def play_video(message, guild):
    while len(queue) > 0:
        url = queue.pop(0)
        print("Bot is now playing from: " + url)
        await message.channel.send("Bot is now playing from: " + url)

        if 'youtube.com' in url:
            print("Doesn't support youtube")
            #await play_youtube_video(guild, url)

        elif 'bitchute.com' in url:
            await play_bitchute_video(guild, url)

        elif 'goyimtv.com' in url:
            await play_goyimtv_video(guild, url)
        
        else:
            print("Invalid URL")

'''
def get_youtube_url(url):
    with youtube_dl.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                return info['url']

async def play_youtube_video(guild, url):
    voice_channel = guild.voice_client.channel
    await voice_channel.guild.change_voice_state(channel=voice_channel, self_mute=False, self_deaf=True)
    video_url = get_youtube_url(url)
    if video_url:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(video_url))
        guild.voice_client.play(source)
        while guild.voice_client.is_playing():
            await asyncio.sleep(1)
    else:
        print("Unable to play video")
'''
        
def get_html_bitchute_video_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            video_url = soup.find('source')['src']
            return video_url
        except Exception:
            traceback.print_exc()
            return None
    else:
        return None

def get_json_bitchute_video_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            print(response.text)
            data = response.json()
            if 'result' in data and 'video_files' in data['result'] and data['result']['video_files']:
                video_url = data['result']['video_files'][0]['file']
                return video_url
            else:
                print("Invalid response data")
                return None
        except Exception:
            traceback.print_exc()
            return None
    else:
        return None
        
async def play_bitchute_video(guild, url):
    voice_channel = guild.voice_client.channel
    await voice_channel.guild.change_voice_state(channel=voice_channel, self_mute=False, self_deaf=True)
    video_url = get_html_bitchute_video_url(url)
    if video_url:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(video_url))
        guild.voice_client.play(source)
        while guild.voice_client.is_playing():
            await asyncio.sleep(1)
    else:
        print("Unable to play video")
        
def get_goyimtv_video_url(url):
    html = requests.get(url).text
    regex = r'sources:\s*\[\s*\{\s*src:\s*"(.*?)"\s*,\s*type:\s*"video/mp4"\s*\}'
    matches = re.search(regex, html)
    if matches:
        video_url = matches.group(1)
        return video_url
    return None

async def play_goyimtv_video(guild, url):
    voice_channel = guild.voice_client.channel
    await voice_channel.guild.change_voice_state(channel=voice_channel, self_mute=False, self_deaf=True)
    #await voice_channel.send('Playing video from GoyimTV...')
    video_url = get_goyimtv_video_url(url)
    if video_url:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(video_url))
        guild.voice_client.play(source)
        while guild.voice_client.is_playing():
            await asyncio.sleep(1)
    else:
        await voice_channel.send('Unable to play video.')


client.run(key)

