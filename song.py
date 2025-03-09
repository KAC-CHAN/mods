from telethon import TelegramClient, events
import yt_dlp
import os
import asyncio


# Replace these with your own values
API_ID = '26788480'
API_HASH = '858d65155253af8632221240c535c314'
BOT_TOKEN = '7222795881:AAFJttyGTf6aKtImylkUW4g0R6ik8ZRpTcI'

client = TelegramClient('song_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/song'))
async def song_handler(event):
    try:
        query = event.text.split('/song', 1)[1].strip()
        if not query:
            return await event.reply("Send song name after /song command")

        # Search and download directly using yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'quiet': True
        }

        await event.reply("🔍 Searching...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, f"ytsearch1:{query}", download=True)
            if not info:
                return await event.reply("❌ Song not found")
            
            entry = info['entries'][0]
            file_path = ydl.prepare_filename(entry).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            caption = f"🎵 {entry['title']}\n👁️ {entry['view_count']:,} views"
            await event.reply(caption, file=file_path)
            
            os.remove(file_path)

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

print("Bot running...")
client.run_until_disconnected()
