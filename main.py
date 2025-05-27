import os
import logging
import requests
from telegram import Bot
from telegram.ext import Application, ContextTypes
from flask import Flask

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
            # स्टाइलिश फॉर्मेटिंग
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
                parse_mode='HTML'  # बेहतर फॉर्मेटिंग के लिए
            )
            logger.info("Formatted quote sent successfully")
        else:
            logger.warning("Failed to fetch quote")
    except Exception as e:
        logger.error(f"Error in send_quote: {e}")

@app.route('/')
def home():
    return "Bot is running! Visit /send-quote to trigger manually"

if __name__ == "__main__":
    # Webhook सेटअप
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # जॉब क्यू सेटअप (हर 5 मिनट)
    job_queue = application.job_queue
    job_queue.run_repeating(send_quote, interval=30, first=10)
    
    # Render पोर्ट कॉन्फ़िगरेशन
    port = int(os.environ.get('PORT', 5000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}"
  )
