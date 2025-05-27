import os
import logging
import requests
from telegram import Bot, Update
from telegram.ext import Application, ContextTypes
from flask import Flask, request

app = Flask(__name__)

# लॉगिंग सेटअप
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# एनवायरनमेंट वेरिएबल
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')  # चैनल ID (-100...) या @username
QUOTE_API = 'https://quotes-api-w4zt.onrender.com/api/quotes/random'
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL')

# Initialize Application
application = Application.builder().token(TELEGRAM_TOKEN).build()

def get_random_quote():
    try:
        response = requests.get(QUOTE_API)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None

async def send_quote(context: ContextTypes.DEFAULT_TYPE):
    try:
        quote_data = get_random_quote()
        if quote_data:
            formatted_message = (
                f"✨ Inspirational Quote\n\n"
                f"╔〇══════════════════════〇\n"
                f"║  {quote_data['author']} ✍️\n"
                f"╚〇══════════════════════〇\n\n"
                f"❝ {quote_data['quote']} ❞\n\n"
                f"〇━━━━━━━━━━━━━━━━━━━━━━━〇\n"
                f"📌 ❖ ARSYNOX\n"
                f"〇━━━━━━━━━━━━━━━━━━━━━━━〇"
            )
            
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=formatted_message,
                parse_mode='HTML'
            )
            logger.info("Quote sent successfully")
    except Exception as e:
        logger.error(f"Send error: {e}")

@app.route('/')
def home():
    return "Bot is running! Use /send-quote to trigger manually"

@app.route('/send-quote', methods=['GET'])
def manual_trigger():
    try:
        # मैन्युअल ट्रिगर के लिए
        application.job_queue.run_once(send_quote, when=0)
        return "Quote will be sent shortly!", 200
    except Exception as e:
        return f"Error: {e}", 500

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Error', 500

def main():
    # जॉब क्यू सेटअप (हर 5 मिनट)
    job_queue = application.job_queue
    job_queue.run_repeating(send_quote, interval=300, first=10)
    
    # Webhook कॉन्फ़िगरेशन
    port = int(os.environ.get('PORT', 10000))  # Render का डिफ़ॉल्ट पोर्ट
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}",
        secret_token=os.getenv('WEBHOOK_SECRET', 'default_secret')
    )

if __name__ == "__main__":
    main()
