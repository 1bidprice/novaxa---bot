"""
Enhanced NOVAXA Telegram Bot  
A professional bot for stock alerts, project monitoring, and automated notifications
"""

import logging
from datetime import datetime
from flask import Flask
import telebot

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="novaxa_bot.log"
)

logger = logging.getLogger(__name__)

# Telegram Bot Token (προσωρινά εδώ, όχι σε .env)
TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"

# Flask app (για Webhook αν χρειαστεί)
app = Flask(__name__)

# Init bot
bot = telebot.TeleBot(TOKEN)

# Dummy project data
projects = {
    "bidprice": {
        "name": "BidPrice",
        "status": "Active",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Πλατφόρμα δημοπρασιών προϊόντων",
        "notes": "Η πρώτη αρχικοποιήθηκε",
        "metrics": {
            "active_listings": 24,
            "new_bids": 12,
            "progress": 75
        }
    },
    "amesis": {
        "name": "Amesis",
        "status": "In Development",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Σύστημα στιγμιαίων ειδοποιήσεων (popup μηνυμάτων)",
        "notes": "Έχουν ξεκινήσει τα API endpoints",
        "metrics": {
            "messages_sent": 156,
            "test_users": 42,
            "progress": 60
        }
    }
}

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Καλώς ήρθες στο NOVAXA v2.0")

# /status command
@bot.message_handler(commands=['status'])
def status(message):
    msg = "Κατάσταση έργων:\n"
    for key, project in projects.items():
        msg += f"\n{project['name']} ({project['status']}) - Πρόοδος: {project['metrics']['progress']}%"
    bot.send_message(message.chat.id, msg)

# Bot polling με αυτόματο καθαρισμό webhook
if __name__ == '__main__':
    import requests
    webhook_url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
    try:
        r = requests.get(webhook_url)
        logger.info("Webhook deleted: %s", r.text)
    except Exception as e:
        logger.error("Webhook delete error: %s", str(e))

    logger.info("Ξεκινάει το NOVAXA bot...")
    bot.polling(none_stop=True)
