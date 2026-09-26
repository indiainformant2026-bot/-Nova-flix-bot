import os
import aiohttp
from aiohttp import web

BOT_TOKEN = "8597463109:AAEZ7PkvubQFr2Q_F0Dl7DiakpnS6_8BS9k"
PORT = int(os.environ.get("PORT", 8080))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def handle(request):
    return web.Response(text="NovaFlix Bot is running perfectly!")

async def telegram_webhook(request):
    try:
        data = await request.json()
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            async with aiohttp.ClientSession() as session:
                if text.startswith("/start"):
                    reply_text = (
                        "👋 Hello!\n\n"
                        "Main NovaFlix ka official File Stream aur Download bot hoon. "
                        "Mujhe koi bhi file bhej, main tujhe Watch Now aur Direct Download link de dunga!"
                    )
                    payload = {"chat_id": chat_id, "text": reply_text}
                    async with session.post(f"{TELEGRAM_API}/sendMessage", json=payload) as resp:
                        pass
                elif "document" in message or "video" in message or "audio" in message:
                    reply_text = (
                        f"📂 **File Received!**\n\n"
                        f"🎬 **Watch Now:** https://t.me/novaflix_link_bot?start=stream\n"
                        f"📥 **Direct Download:** https://t.me/novaflix_link_bot?start=download"
                    )
                    payload = {"chat_id": chat_id, "text": reply_text, "parse_mode": "Markdown"}
                    async with session.post(f"{TELEGRAM_API}/sendMessage", json=payload) as resp:
                        pass
        return web.Response(text="OK")
    except Exception as e:
        return web.Response(text=str(e), status=500)

async def on_startup(app):
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}") as resp:
                print("Webhook set status:", await resp.text())

if __name__ == "__main__":
    web_app = web.Application()
    web_app.router.add_get("/", handle)
    web_app.router.add_post(f"/{BOT_TOKEN}", telegram_webhook)
    web_app.on_startup.append(on_startup)
    
    web.run_app(web_app, host="0.0.0.0", port=PORT)
