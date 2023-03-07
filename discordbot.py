import discord
import youtube_dl
import json
import asyncio

queue = []

client = discord.Client(intents=discord.Intents.all())

# Open the JSON file and load its contents
with open('key.json') as f:
    data = json.load(f)

# Access the values associated with the keys
key = data['key']

queue = []

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!play'):
        url = message.content.split()[1]
        if 'youtube.com' or 'youtu.be' in url:
            await message.channel.send('Adding video to queue...')
            queue.append(url)
            if not message.guild.voice_client.is_playing():
                await play_video(message.guild)
        elif 'bitchute.com' in url:
            await message.channel.send('Adding video to queue...')
            queue.append(url)
            if not message.guild.voice_client.is_playing():
                await play_video(message.guild)
        else:
            await message.channel.send('Invalid URL')

    if message.content == '!pause':
        if message.guild.voice_client.is_playing():
            message.guild.voice_client.pause()
            await message.channel.send('Playback paused.')
        else:
            await message.channel.send('Nothing is playing at the moment.')

    if message.content == '!skip':
        if message.guild.voice_client.is_playing():
            message.guild.voice_client.stop()
            await message.channel.send('Skipping to the next video.')
            await play_video(message.guild)
        else:
            await message.channel.send('Nothing is playing at the moment.')

async def play_video(guild):
    while len(queue) > 0:
        url = queue.pop(0)
        if 'youtube.com' in url:
            await guild.voice_client.disconnect()
            await asyncio.sleep(1)
            channel = guild.get_channel(123456789012345678) # replace with voice channel ID
            await channel.connect()
            await channel.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
            await channel.send('Playing video from YouTube...')
            with youtube_dl.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                URL = info['url']
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(URL))
                channel.guild.voice_client.play(source)
                while channel.guild.voice_client.is_playing():
                    await asyncio.sleep(1)
        elif 'bitchute.com' in url:
            await guild.voice_client.disconnect()
            await asyncio.sleep(1)
            channel = guild.get_channel(123456789012345678) # replace with voice channel ID
            await channel.connect()
            await channel.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
            await channel.send('Playing video from BitChute...')
            with youtube_dl.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                URL = info['url']
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(URL))
                channel.guild.voice_client.play(source)
                while channel.guild.voice_client.is_playing():
                    await asyncio.sleep(1)
    await guild.voice_client.disconnect()

client.run(key)
