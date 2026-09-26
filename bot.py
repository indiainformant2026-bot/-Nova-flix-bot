import os
import aiohttp
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

BOT_TOKEN = "8597463109:AAEZ7PKvub0GRF2Q_FODI7DiakpnS6_8BS9k"
DATABASE_URL = "mongodb+srv://Indiainformant2026_db_user:NE7KxMu9PwA1gI8k@cluster0.psj30qj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
PORT = int(os.environ.get("PORT", "10000"))
RENDER_URL = "https://nova-flix-bot.onrender.com"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# MongoDB Connection Setup
mongo_client = AsyncIOMotorClient(DATABASE_URL)
db = mongo_client["NovaFlixDB"]
files_collection = db["files"]

async def handle(request):
    path = request.path
    # File Stream Handle karne ke liye
    if path.startswith("/stream/"):
        file_id_str = path.split("/")[-1]
        try:
            file_doc = await files_collection.find_one({"_id": ObjectId(file_id_str)})
            if file_doc:
                tg_file_id = file_doc["file_id"]
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{TELEGRAM_API}/getFile?file_id={tg_file_id}") as resp:
                        res_data = await resp.json()
                        if res_data.get("ok"):
                            file_path = res_data["result"]["file_path"]
                            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                            raise web.HTTPFound(download_url)
        except web.HTTPFound:
            raise
        except Exception as e:
            print(f"Error fetching file: {e}")
        return web.Response(text="File not found or expired", status=404)
        
    return web.Response(text="NovaFlix Ultra Pro Max Server is Active and Running!")

async def telegram_webhook(request):
    try:
        data = await request.json()
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            
            async with aiohttp.ClientSession() as session:
                # Text Message /start handling
                if "text" in message:
                    text = message["text"]
                    if text == "/start":
                        reply_text = "Main NovaFlix ka official bot hoon!\nMujhe koi bhi movie file ya video bhejo, main tumhe direct download link bana kar dunga."
                        payload = {"chat_id": chat_id, "text": reply_text}
                        await session.post(f"{TELEGRAM_API}/sendMessage", json=payload)
                        
                # Document ya Video handling
                elif "document" in message or "video" in message:
                    media = message.get("document") or message.get("video")
                    file_id = media["file_id"]
                    file_name = media.get("file_name", "Unknown_File")
                    
                    # Save to MongoDB
                    db_doc = {
                        "file_id": file_id,
                        "file_name": file_name
                    }
                    result = await files_collection.insert_one(db_doc)
                    db_id = str(result.inserted_id)
                    
                    # Generate Link
                    download_link = f"{RENDER_URL}/stream/{db_id}"
                    reply_text = f"**File Name:** {file_name}\n\n**Direct Download Link:**\n{download_link}"
                    
                    payload = {"chat_id": chat_id, "text": reply_text}
                    await session.post(f"{TELEGRAM_API}/sendMessage", json=payload)
                    
        return web.Response(status=200)
    except Exception as e:
        print(f"Error in webhook: {e}")
        return web.Response(status=200)

async def on_startup(app):
    # Render start hote hi khud Webhook set kar dega
    webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
    async with aiohttp.ClientSession() as session:
        await session.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}")
        print("Webhook Automatically Set via Code!")

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get("/", handle)
    app.router.add_get("/stream/{id}", handle)
    app.router.add_post(f"/{BOT_TOKEN}", telegram_webhook)
    app.on_startup.append(on_startup)
    web.run_app(app, host="0.0.0.0", port=PORT)
