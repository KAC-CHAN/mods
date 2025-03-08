import os
import requests
from io import BytesIO
from telethon import TelegramClient, events, Button
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "26788480"))
API_HASH = os.getenv("API_HASH", "858d65155253af8632221240c535c314")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7224277474:AAERIx4M_R62CI6dX5ouwuZpPZ6MerZG4Nw")
STABILITY_KEY = os.getenv("STABILITY_KEY", "sk-f4HmOQvBhKYcYdJAhmpStu1y7A22d9T1wlQOYZsPIkxZtl5a")

client = TelegramClient('ai_art_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def generate_art(prompt: str) -> bytes:
    try:
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "authorization": f"Bearer {STABILITY_KEY}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "jpeg",
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"API Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "🎨 **AI Art Bot**\n\n"
        "Send /generate followed by your prompt to create art!\n"
        "Example: `/generate futuristic cityscape, neon colors, cyberpunk theme`\n\n"
        "You can include details like:\n"
        "- Color schemes\n"
        "- Art style\n"
        "- Mood/atmosphere\n"
        "- Specific elements to include",
        link_preview=False
    )

@client.on(events.NewMessage(pattern='/generate'))
async def generate_handler(event):
    prompt = event.raw_text[len('/generate'):].strip()
    if not prompt:
        await event.reply("Please provide a prompt after /generate")
        return
    
    msg = await event.reply("🖌️ Generating your art... (This may take 10-30 seconds)")
    
    image_data = await generate_art(prompt)
    
    if not image_data:
        await msg.edit("❌ Failed to generate art. Please try again with a different prompt.")
        return
    
    await client.send_file(
        event.chat_id,
        BytesIO(image_data),
        caption=f"🎨 **Generated Artwork**\n\n**Prompt:** {prompt}",
        buttons=[
            [Button.inline("🔄 Generate Variation", data=f"variation:{prompt}")],
            [Button.inline("✨ Enhance", data=f"enhance:{prompt}")]
        ]
    )
    await msg.delete()

@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode().split(":", 1)
    action = data[0]
    prompt = data[1] if len(data) > 1 else ""
    
    await event.answer("Generating...")
    
    if action == "variation":
        new_prompt = f"{prompt} #variation"
    elif action == "enhance":
        new_prompt = f"{prompt} #ultra_detail #8k #sharp_focus"
    else:
        return
    
    image_data = await generate_art(new_prompt)
    
    if not image_data:
        await event.reply("❌ Failed to generate art. Please try again.")
        return
    
    await client.send_file(
        event.chat_id,
        BytesIO(image_data),
        caption=f"🎨 **{'Variation' if action == 'variation' else 'Enhanced'} Artwork**\n\n**Prompt:** {new_prompt}",
        buttons=[
            [Button.inline("🔄 Generate Variation", data=f"variation:{new_prompt}")],
            [Button.inline("✨ Enhance", data=f"enhance:{new_prompt}")]
        ]
    )

if __name__ == '__main__':
    print("Bot started!")
    client.run_until_disconnected()
