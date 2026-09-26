import os
import aiohttp
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient
import bson

BOT_TOKEN = "8597463109:AAEZ7PkvubQFr2Q_F0Dl7DiakpnS6_8BS9k"
DATABASE_URL = "mongodb+srv://Indiainformant2026_db_user:NE7KxMu9PwA1gI8k@cluster0.psj30qj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Render के लॉग्स के अनुसार पोर्ट 10000 यूज़ हो रहा है
PORT = int(os.environ.get("PORT", 10000)) 
RENDER_URL = "https://nova-flix-bot.onrender.com"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# MongoDB Connection Setup
mongo_client = AsyncIOMotorClient(DATABASE_URL)
db = mongo_client["NovaFlixDB"]
files_collection = db["files"]

async def handle(request):
    path = request.path
    if path.startswith("/stream/"):
        file_id_str = path.split("/")[-1]
        try:
            file_doc = await files_collection.find_one({"_id": bson.ObjectId(file_id_str)})
            if file_doc:
                tg_file_id = file_doc["file_id"]
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{TELEGRAM_API}/getFile?file_id={tg_file_id}") as resp:
                        res_data = await resp.json()
                        if res_data.get("ok"):
                            file_path = res_data["result"]["file_path"]
                            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                            raise web.HTTPFound(download_url)
        except Exception as e:
            print(f"Error fetching file: {e}")
        return web.Response(text="File not found or expired!", status=404)
    
    return web.Response(text="NovaFlix Ultra Pro Max Server is active and running!")

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
                        "👋 Welcome to **NovaFlix Ultra Pro Max**!\n\n"
                        "मुझे कोई भी मूवी या वीडियो फ़ाइल भेज, मैं तुझे तुरंत रियल **Watch Now** और **Direct Download** लिंक बना कर दूंगा!"
                    )
                    payload = {"chat_id": chat_id, "text": reply_text, "parse_mode": "Markdown"}
                    await session.post(f"{TELEGRAM_API}/sendMessage", json=payload)
                else:
                    media = message.get("document") or message.get("video") or message.get("audio")
                    if media:
                        file_id = media.get("file_id")
                        file_name = media.get("file_name", "NovaFlix_Video.mp4")
                        file_size_bytes = media.get("file_size", 0)
                        file_size = round(file_size_bytes / (1024 * 1024), 2) if file_size_bytes else 0.0
                        
                        # Database में फ़ाइल सेव करो
                        inserted = await files_collection.insert_one({
                            "file_id": file_id,
                            "file_name": file_name,
                            "file_size": file_size
                        })
                        db_id = str(inserted.inserted_id)
                        
                        stream_link = f"{RENDER_URL}/stream/{db_id}"
                        download_link = f"{RENDER_URL}/stream/{db_id}"
                        
                        reply_text = (
                            f"📂 **File Name:** `{file_name}`\n"
                            f"📊 **Size:** `{file_size} MB`\n\n"
                            f"👇 **आपके असली लिंक्स तैयार हैं:**\n"
                            f"🎬 [Watch Now (Stream)]({stream_link})\n"
                            f"📥 [Direct Download]({download_link})"
                        )
                        payload = {
                            "chat_id": chat_id, 
                            "text": reply_text, 
                            "parse_mode": "Markdown",
                            "disable_web_page_preview": True
                        }
                        await session.post(f"{TELEGRAM_API}/sendMessage", json=payload)
        return web.Response(text="OK")
    except Exception as e:
        print(f"Webhook processing error: {e}")
        return web.Response(text="Error processing request", status=500)

async def on_startup(app):
    # यह फंक्शन सर्वर स्टार्ट होते ही वेबहुक रजिस्टर करेगा
    webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}") as resp:
            result = await resp.text()
            print(f"Webhook Registration Status: {result}")

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get("/", handle)
    app.router.add_get("/stream/{id}", handle)
    # वेबहुक के लिए POST रिक्वेस्ट को हैंडल करना
    app.router.add_post(f"/{BOT_TOKEN}", telegram_webhook)
    
    # स्टार्टअप फंक्शन को सही तरीके से जोड़ना
    app.on_startup.append(on_startup)
    
    web.run_app(app, host="0.0.0.0", port=PORT)
