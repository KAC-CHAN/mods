import os
import asyncio
from pyrogram import Client, filters
from mega import Mega

# Bot configuration
API_ID = '26788480'
API_HASH = '858d65155253af8632221240c535c314'
BOT_TOKEN = '7224277474:AAE90HkXGo29T2A9UsdQ7P53RL5dihtzemo'

# Initialize Pyrogram client
app = Client("mega_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Create temporary directory
TEMP_DIR = "temp_downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

def download_from_mega(url: str) -> str:
    """Download file from Mega.nz link and return file path"""
    mega = Mega().login()  # Anonymous login
    file_name = mega.download_url(url, TEMP_DIR)
    return os.path.join(TEMP_DIR, file_name)

@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    if "mega.nz" in message.text:
        try:
            # Send initial response
            msg = await message.reply("⏳ Downloading from Mega.nz...")
            
            # Download file in background thread
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(
                None, download_from_mega, message.text
            )
            
            # Send downloaded file
            await message.reply_document(
                document=file_path,
                caption="Here's your file!",
                progress=lambda current, total: print(f"Uploaded {current * 100 / total:.1f}%")
            )
            
            # Cleanup
            os.remove(file_path)
            await msg.edit("✅ File sent successfully!")
            
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    print("Bot started...")
    app.run()
