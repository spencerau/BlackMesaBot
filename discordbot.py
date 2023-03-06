import discord
import asyncio
import urllib.parse
import urllib.request
import re
import youtube_dl
import json

client = discord.Client()

# Open the JSON file and load its contents
with open('data.json') as f:
    data = json.load(f)

# Access the values associated with the keys
key = data['key']

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.content.startswith('>play '):
        query = message.content[6:]
        query_string = urllib.parse.urlencode({'search_query': query})
        html_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
        search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())
        url = 'http://www.youtube.com/watch?v=' + search_results[0]
        voice_channel = message.author.voice.channel
        if not voice_channel:
            await message.channel.send('You are not connected to a voice channel.')
            return
        voice_client = await voice_channel.connect()
        with youtube_dl.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            voice_client.play(discord.FFmpegPCMAudio(URL))
        await message.channel.send(f'Now playing: {info["title"]}')

client.run(key)