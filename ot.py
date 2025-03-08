from telethon import TelegramClient, events
from pytube import Search, YouTube
import os
import asyncio

# Replace these with your own values
API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
BOT_TOKEN = 'YOUR_BOT_TOKEN'

client = TelegramClient('song_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/song'))
async def song_downloader(event):
    try:
        song_name = event.raw_text.split('/song', 1)[1].strip()
        if not song_name:
            await event.reply("Please enter a song name after /song command!")
            return

        # Search for the song on YouTube
        search = Search(song_name)
        results = list(search.results)
        
        if not results:
            await event.reply("No results found 😞")
            return

        # Get first result
        video = results[0]
        audio_stream = video.streams.filter(only_audio=True).first()
        
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
        
        # Send audio with metadata
        caption = f"🎵 **Title:** {video.title}\n👁️ **Views:** {video.views:,}"
        await event.reply(caption, file=new_file)
        
        # Clean up
        os.remove(new_file)

    except Exception as e:
        await event.reply(f"An error occurred: {str(e)}")

print("Bot is running...")
client.run_until_disconnected()
