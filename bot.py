
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 26788480  # Replace with your API ID
API_HASH = "858d65155253af8632221240c535c314"  # Replace with your API Hash
BOT_TOKEN = "7224277474:AAERIx4M_R62CI6dX5ouwuZpPZ6MerZG4Nw"  # Replace with your Bot Token
HF_API_KEY = "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"  # Get from huggingface.co

app = Client("ai_art_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Stable Diffusion API endpoint
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

async def generate_art(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            with open("generated_art.jpg", "wb") as f:
                f.write(response.content)
            return "generated_art.jpg"
        else:
            return None
            
    except Exception as e:
        print(f"API Error: {e}")
        return None

@app.on_message(filters.command(["start"]))
async def start(client, message: Message):
    await message.reply_text(
        "🎨 **AI Art Bot**\n\n"
        "Send /generate followed by your prompt to create art!\n"
        "Example: `/generate futuristic cityscape, neon colors, cyberpunk theme`\n\n"
        "You can include details like:\n"
        "- Color schemes\n"
        "- Art style\n"
        "- Mood/atmosphere\n"
        "- Specific elements to include"
    )

@app.on_message(filters.command(["generate"]))
async def generate(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a prompt after /generate")
    
    prompt = " ".join(message.command[1:])
    msg = await message.reply_text("🖌️ Generating your art... (This may take 10-30 seconds)")
    
    art_path = await generate_art(prompt)
    
    if not art_path:
        return await msg.edit_text("❌ Failed to generate art. Please try again with a different prompt.")
    
    await client.send_photo(
        message.chat.id,
        art_path,
        caption=f"🎨 **Generated Artwork**\n\n**Prompt:** {prompt}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Generate Variation", callback_data=f"variation:{prompt}")],
            [InlineKeyboardButton("✨ Enhance", callback_data=f"enhance:{prompt}")]
        ])
    )
    await msg.delete()
    os.remove(art_path)

@app.on_callback_query()
async def callback_handler(client, callback):
    action, prompt = callback.data.split(":", 1)
    
    await callback.answer("Generating...")
    await callback.message.edit_reply_markup(None)
    
    if action == "variation":
        new_prompt = prompt + " #variation"
    elif action == "enhance":
        new_prompt = prompt + " #high_detail #4k #sharp"
    
    art_path = await generate_art(new_prompt)
    
    if not art_path:
        return await callback.message.reply_text("❌ Failed to generate art. Please try again.")
    
    await client.send_photo(
        callback.message.chat.id,
        art_path,
        caption=f"🎨 **{'Variation' if action == 'variation' else 'Enhanced'} Artwork**\n\n**Prompt:** {new_prompt}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Generate Variation", callback_data=f"variation:{new_prompt}")],
            [InlineKeyboardButton("✨ Enhance", callback_data=f"enhance:{new_prompt}")]
        ])
    )
    os.remove(art_path)

if __name__ == "__main__":
    print("Bot Started!")
    app.run()
