import os
import aiohttp
from aiohttp import web
import motor.motor_asyncio
import asyncio

# --- Configuration (Your Ultra Pro Max Setup) ---
BOT_TOKEN = "8597463109:AAEZ7PKvubQFr2Q_FODI7DiakpnSd_8B5hk" # Replace with your actual token if different
# Password has been URL-encoded: % -> %25, # -> %23
DATABASE_URL = "mongodb+srv://indainformant2026:hZpwBk5%253Nn%23FJa@cluster0.q0z94.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
RENDER_URL = "https://nova-flix-bot.onrender.com"
PORT = int(os.environ.get("PORT", 10000))

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# --- Database Initialization ---
client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client["nova_flix_db"]
collection = db["users"]

# --- Helper Function: Send Message ---
async def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()

# --- Webhook Handler ---
async def telegram_webhook(request):
    try:
        data = await request.json()
        print("Received update:", data)

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            # /start Command Logic
            if text == "/start":
                # Save user to DB (Upsert prevents duplicates)
                await collection.update_one(
                    {"chat_id": chat_id},
                    {"$set": {"chat_id": chat_id, "active": True}},
                    upsert=True
                )
                
                welcome_msg = "🌟 Welcome to NovaFlix! 🌟\n\nआपका डेटाबेस कनेक्शन अब बिल्कुल परफेक्ट तरीके से काम कर रहा है!"
                await send_message(chat_id, welcome_msg)

        # Always return 200 OK so Telegram stops retrying
        return web.Response(text="OK", status=200)

    except Exception as e:
        print(f"Error in webhook processing: {e}")
        # Return 200 even on error to prevent Telegram from spamming the webhook
        return web.Response(text="Error handled", status=200)

# --- Health Check (To keep Render happy) ---
async def health_check(request):
    return web.Response(text="NovaFlix Bot is Live and Running smoothly!", status=200)

# --- Application Setup ---
async def init_app():
    app = web.Application()
    app.router.add_post('/telegram', telegram_webhook)
    app.router.add_get('/', health_check)
    return app

# --- Auto Webhook Registration ---
async def set_webhook():
    webhook_url = f"{RENDER_URL}/telegram"
    url = f"{TELEGRAM_API}/setWebhook?url={webhook_url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            print("Webhook Registration Status:", result)

# --- Run Server ---
if __name__ == "__main__":
    # Register webhook before starting the server
    asyncio.run(set_webhook())
    
    # Start the web server
    app = asyncio.run(init_app())
    web.run_app(app, host="0.0.0.0", port=PORT)
