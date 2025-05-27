import os
import logging
import requests
from telegram import Bot, Update
from telegram.ext import Application, ContextTypes
from flask import Flask, request

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')  # Format: -1001234567890 or @channelname
QUOTE_API = 'https://quotes-api-w4zt.onrender.com/api/quotes/random'
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL')

# Initialize Telegram Bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

def get_formatted_quote():
    try:
        response = requests.get(QUOTE_API)
        response.raise_for_status()
        data = response.json()
        
        return (
            f"✨ Inspirational Quote\n\n"
            f"╔〇══════════════════════〇\n"
            f"║  {data['author']} ✍️\n"
            f"╚〇══════════════════════〇\n\n"
            f"❝ {data['quote']} ❞\n\n"
            f"〇━━━━━━━━━━━━━━━━━━━━━━━〇\n"
            f"📌 ❖ ARSYNOX\n"
            f"〇━━━━━━━━━━━━━━━━━━━━━━━〇"
        )
    except Exception as e:
        logger.error(f"Quote Error: {e}")
        return None

async def send_quote(context: ContextTypes.DEFAULT_TYPE):
    try:
        message = get_formatted_quote()
        if message:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode='HTML'
            )
            logger.info("Quote sent to channel")
    except Exception as e:
        logger.error(f"Sending Failed: {e}")

@app.route('/')
def home():
    return "🚀 Bot Active | Use /send-quote to trigger manually"

@app.route('/send-quote', methods=['GET'])
def manual_trigger():
    try:
        application.job_queue.run_once(send_quote, when=0)
        return "✅ Quote queued!", 200
    except Exception as e:
        return f"❌ Error: {e}", 500

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Webhook Error: {e}")
        return 'ERROR', 500

def main():
    # Schedule quotes every 5 minutes
    job_queue = application.job_queue
    job_queue.run_repeating(
        callback=send_quote,
        interval=300,
        first=10
    )

    # Webhook configuration for Render
    port = int(os.environ.get('PORT', 10000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}",
        secret_token=os.getenv('WEBHOOK_SECRET')
    )

if __name__ == "__main__":
    main()
