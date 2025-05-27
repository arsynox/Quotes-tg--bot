import os
import asyncio
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Environment variables
TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # e.g. '@yourchannel' or -1001234567890

bot = Bot(token=TOKEN)
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your Inspirational Quote Bot.")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "🚀 Inspirational Quotes Bot is running!"

def format_quote(data):
    author = data.get("author", "Unknown")
    quote = data.get("quote", "No quote available.")
    return (
        f"✨ Inspirational Quote\n\n"
        f"╔〇══════════════════════〇\n"
        f"║  {author} ✍️\n"
        f"╚〇══════════════════════〇\n\n"
        f"❝ {quote} ❞\n\n"
        f"〇━━━━━━━━━━━━━━━━━━━━━━━〇\n"
        f"📌 ❖ ARSYNOX\n"
        f"〇━━━━━━━━━━━━━━━━━━━━━━━〇"
    )

def fetch_quote():
    try:
        res = requests.get("https://quotes-api-w4zt.onrender.com/api/quotes/random", timeout=5)
        if res.status_code == 200:
            return format_quote(res.json())
        else:
            return "Could not fetch quote."
    except Exception as e:
        return f"Error fetching quote: {e}"

async def auto_send_quote():
    while True:
        quote = fetch_quote()
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=quote)
        except Exception as e:
            print(f"[ERROR] Failed to send quote: {e}")
        await asyncio.sleep(300)

@app.before_first_request
def setup():
    bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TOKEN}")
    asyncio.create_task(auto_send_quote())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
