import os
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 31419331
API_HASH = "B74d877e3b10ecd8038cbbca3b20a21d"
BOT_TOKEN = "8597463109:AAEZ7PkvubQFr2Q_F0Dl7DiakpnS6_8BS9k"

PORT = int(os.environ.get("PORT", 8080))

# Pyrogram Client setup
app = Client(
    "NovaFlixFinalBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

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

# Web server taaki Render ka port check pass ho jaye
async def handle(request):
    return web.Response(text="NovaFlix Bot is running successfully!")

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Aiohttp web server start karo
        web_app = web.Application()
        web_app.router.add_get("/", handle)
        runner = web_AppRunner(web_app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        print("Web server started on port", PORT)
        
        # Pyrogram bot start karo
        await app.start()
        print("Bot started successfully!")
        await asyncio.Event().wait()

    asyncio.run(main())
