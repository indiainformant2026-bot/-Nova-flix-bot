import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 31419331
API_HASH = "B74d877e3b10ecd8038cbbca3b20a21d"
BOT_TOKEN = "8597463109:AAEZ7PkvubQFr2Q_F0Dl7DiakpnS6_8BS9k"
DATABASE_URL = "mongodb+srv://Indiainformant2026_db_user:NE7KxMu9PwA1gI8k@cluster0.psj30qj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

PORT = int(os.environ.get("PORT", 8080))

app = Client(
    "NovaFlixFinalBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Render ke liye chota web server
async def handle(request):
    return web.Response(text="NovaFlix Bot is active and running!")

async def web_server():
    web_app = web.Application()
    web_app.router.add_get("/", handle)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text(
        f"👋 Hello **{message.from_user.first_name}**!\n\n"
        "Main NovaFlix ka official File Stream aur Download bot hoon. "
        "Mujhe koi bhi movie file bhej, main tujhe turant **Watch Now** aur **Direct Download** link de dunga!",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🚀 NovaFlix App", url="https://t.me/novaflix_link_bot")]]
        )
    )

@app.on_message(filters.document | filters.video | filters.audio)
async def media_handler(client, message: Message):
    media = message.document or message.video or message.audio
    file_name = media.file_name if hasattr(media, "file_name") else "Video_File.mp4"
    file_size = round(media.file_size / (1024 * 1024), 2)
    
    stream_link = f"https://t.me/novaflix_link_bot?start=stream_{message.id}"
    download_link = f"https://t.me/novaflix_link_bot?start=download_{message.id}"
    
    caption = (
        f"📂 **File Name:** `{file_name}`\n"
        f"📊 **Size:** `{file_size} MB`\n\n"
        f"👇 **Apne links yahan se copy karein:**"
    )
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Watch Now (Stream)", url=stream_link),
            InlineKeyboardButton("📥 Direct Download", url=download_link)
        ]
    ])
    
    await message.reply_text(caption, reply_markup=reply_markup, quote=True)

async def main():
    await app.start()
    await web_server()
    print("Bot aur Web Server successfully start ho gaye hain!")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
