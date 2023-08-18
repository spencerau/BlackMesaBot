import discord
import json
import asyncio
import requests
import logging
import yt_dlp
import moviepy.editor as mp
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)  # Change to logging.DEBUG for more detailed logging

# Open the JSON file and load its contents
with open('key.json') as f:
    data = json.load(f)

# Access the values associated with the keys
key = data['key']

import json

# Open the JSON file and load its contents
with open('discord_ids.json', 'r') as f:
    data = json.load(f)

# Extract the list of numerical IDs from the JSON data
id_list = [item['id'] for item in data if isinstance(item['id'], (int, float))]

#print("ID LIST:")
print(id_list)
queue = []
videoSites = ['youtube.com', 'youtu.be', 'bitchute.com']
censorList = []

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    
    user_id = message.author.id
    #print("user_id = " + str(user_id))

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
                await play(message, message.guild)
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
            await play_video(message, message.guild)
        else:
            await message.channel.send('Nothing is playing at the moment.')

    elif message.content == '!help':
        # implement listing out commands with descriptions
        print("help command - need to implement")

    elif message.content == '!clearqueue':
        queue.clear()
        await message.channel.send('Queue cleared.')

    elif message.content == '!queue':
        # implement showing the queue
        print("queue command - need to implement")

    elif 'bjp' in message.content.lower():
        #print("phrase BJP seen")
        if user_id in id_list:
            #print("user_id is in the id list")
            if user_id == id_list[0]:
                await message.channel.send("Help Support Your Local BJP Branch in Delhi!")
                await message.channel.send("https://delhi.bjp.org/")
            elif user_id == id_list[1] or user_id == id_list[3]:
                await message.channel.send("Help Support Your Local BJP Branch in Uttar Pradesh")
                await message.channel.send("https://up.bjp.org/")
            elif user_id == id_list[2]:
                await message.channel.send("Help Support Your Local BJP Branch in Rajasthan")
                await message.channel.send("https://rajasthanbjp.org/")
        # link to donate to BJP site

    elif 'dog' in message.content.lower():
        if user_id == id_list[4]:
            await message.channel.send("https://www.vietworldkitchen.com/blog/tag/vietnamese-dog-recipes")

    elif 'alex jones' in message.content.lower():
        await message.channel.send("https://www.infowarsstore.com/")
        # 77 href 
        # href="url"

async def play(message, guild):
    while len(queue) > 0:
        url = queue.pop(0)
        print("Bot is now playing from: " + url)
        await message.channel.send("Bot is now playing from: " + url)

        if 'youtu' in url or 'youtube' in url:
            await play_video(guild, url, "youtube")

        elif 'bitchute.com' in url:
            await play_video(guild, url, "bitchute")

        elif 'vimeo.com' in url:
            await play_video(guild, url, "vimeo")
        
        else:
            print("Invalid URL")

async def get_video_url(url, platform):
    if platform == 'youtube':
        ydl_opts = {
            'quiet': True,  # Enable quiet mode
            'format': 'best'  # Download the best available quality
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
            video_url = info_dict.get('url', None)
            #print("YouTube Video URL:", video_url)  # Print the video URL
    elif platform == 'bitchute' and 'bitchute.com' in url:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            source = soup.find('source')
            video_url = source.get('src', None)
            print("Bitchute Video URL:", video_url)  # Print the video URL
        else:
            video_url = None
    else:
        video_url = None
    return video_url

async def play_video(guild, url, platform):
    voice_channel = guild.voice_client.channel
    await voice_channel.guild.change_voice_state(channel=voice_channel, self_mute=False, self_deaf=True)
    video_url = await get_video_url(url, platform)  # Await the asynchronous function
    
    if video_url:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(video_url))
        guild.voice_client.play(source)
        while guild.voice_client.is_playing():
            await asyncio.sleep(1)
    else:
        print("Unable to play video")

client.run(key)
