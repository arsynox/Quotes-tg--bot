import os
import time
import asyncio
import threading
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

def fetch_quote():
    try:
        response = requests.get("https://quotes-api-w4zt.onrender.com/api/quotes/random")
        if response.status_code == 200:
            data = response.json()
            quote = data.get("quote")
            author = data.get("character", "Unknown")
            return quote, author
        return None, None
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return None, None

def format_quote_message(quote, author):
    return f"""✨ Inspirational Quote

╔〇══════════════════════〇
║  {author} ✍️
╚〇══════════════════════〇

❝ {quote} ❞

〇━━━━━━━━━━━━━━━━━━━━━━━〇
📌 ❖ ARSYNOX
〇━━━━━━━━━━━━━━━━━━━━━━━〇"""

async def auto_send_quote():
    while True:
        quote, author = fetch_quote()
        if quote and author:
            message = format_quote_message(quote, author)
            try:
                await application.bot.send_message(chat_id=CHANNEL_ID, text=message)
                print("Quote sent successfully!")
            except Exception as e:
                print(f"Error sending quote: {e}")
        else:
            print("Failed to fetch quote.")
        await asyncio.sleep(300)  # 5 minutes

def start_auto_quote_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(auto_send_quote())

@app.before_first_request
def activate_job():
    thread = threading.Thread(target=start_auto_quote_thread)
    thread.start()
    webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
    asyncio.run(application.bot.set_webhook(webhook_url))

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Quote Bot is Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
