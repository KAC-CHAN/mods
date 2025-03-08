


from telethon import TelegramClient, events
from youtube_search import YoutubeSearch
from pytubefix import YouTube
import os
import asyncio

# Replace these with your own values
API_ID = '26788480'
API_HASH = '858d65155253af8632221240c535c314'
BOT_TOKEN = '7222795881:AAFJttyGTf6aKtImylkUW4g0R6ik8ZRpTcI'

client = TelegramClient('song_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/song'))
async def song_downloader(event):
    try:
        song_name = event.raw_text.split('/song', 1)[1].strip()
        if not song_name:
            await event.reply("Please enter a song name after /song command!")
            return

        # Search YouTube using youtube-search-python
        results = YoutubeSearch(song_name, max_results=1).to_dict()
        if not results:
            await event.reply("No results found 😞")
            return

        video_id = results[0]['id']
        yt_url = f"https://youtube.com/watch?v={video_id}"
        
        # Create YouTube object
        yt = YouTube(yt_url)
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if not audio_stream:
            await event.reply("Couldn't find audio stream 😢")
            return

        # Download audio
        await event.reply("Downloading your song... ⏳")
        download_path = await asyncio.to_thread(audio_stream.download, output_path="downloads")
        
        # Rename file to .mp3
        base = os.path.splitext(download_path)[0]
        new_file = base + ".mp3"
        os.rename(download_path, new_file)
        
        # Get video details
        views = f"{int(yt.views):,}"
        title = yt.title

        # Send audio with metadata
        caption = f"🎵 **Title:** {title}\n👁️ **Views:** {views}"
        await event.reply(caption, file=new_file)
        
        # Clean up
        os.remove(new_file)

    except Exception as e:
        await event.reply(f"An error occurred: {str(e)}")

print("Bot is running...")
client.run_until_disconnected()
