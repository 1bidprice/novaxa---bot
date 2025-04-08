import telebot
import logging
from flask import Flask, request
from datetime import datetime
import threading
import schedule
import time

# ================== CONFIG ===================
BOT_TOKEN = "7658672268:AAHjzU-RICSnT44JKOJyAW1YPhrglUZBTHk"
WEBHOOK_URL = "https://novaxa.onrender.com/webhook"
# =============================================

# Logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
)
logger = logging.getLogger()

# Init bot + app
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')
app = Flask(__name__)
user_data = {}

# Dummy projects
projects = {
    "bidprice": {
        "name": "BidPrice",
        "status": "Active",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Η πλατφόρμα BidPrice είναι σε λειτουργία και δέχεται προσφορές.",
        "logs": ["Η πλατφόρμα ενεργοποιήθηκε.", "Ολοκληρώθηκε η MVP δοκιμή."],
        "metrics": {"active_listings": 24, "new_bids": 12, "progress": 75}
    },
    "amesis": {
        "name": "Amesis",
        "status": "In Development",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Η εφαρμογή Amesis είναι εργαλείο για επείγοντα pop-up μηνύματα.",
        "logs": ["Ξεκίνησε η διεπαφή.", "API ενσωματώθηκε."],
        "metrics": {"messages_sent": 156, "recipients": 42, "progress": 60}
    }
}

# ===== Telegram Commands =====
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Καλωσόρισες στο NOVAXA Bot!\nΧρησιμοποίησε /help για εντολές.")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "*Εντολές:*\n/start\n/help\n/status\n/log\n/getid", parse_mode='Markdown')

@bot.message_handler(commands=['getid'])
def getid_command(message):
    bot.reply_to(message, f"Το Telegram ID σου είναι: `{message.from_user.id}`")

@bot.message_handler(commands=['status'])
def status_command(message):
    text = "*Κατάσταση Έργων:*"
    for pid, data in projects.items():
        emoji = "🟢" if data['status'] == "Active" else "🔵"
        text += f"\n\n{emoji} *{data['name']}*\nΚατάσταση: {data['status']}\nΠρόοδος: {data['metrics'].get('progress', 0)}%"
    bot.reply_to(message, text)

@bot.message_handler(commands=['log'])
def log_command(message):
    try:
        with open("log.txt", "r", encoding="utf-8") as f:
            log_lines = f.readlines()[-20:]
            response = "*Τελευταία Logs:*\n" + "".join(log_lines)
    except:
        response = "Δεν υπάρχουν logs."
    bot.reply_to(message, response, parse_mode='Markdown')

# ===== Flask Routes =====
@app.route('/')
def index():
    return "NOVAXA bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return 'ok', 200
    return 'forbidden', 403

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    try:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        return f"Webhook set to {WEBHOOK_URL}", 200
    except Exception as e:
        return f"Error: {e}", 500

# ======= START Flask App ========
if __name__ == '__main__':
    import os
    from gunicorn.app.base import BaseApplication

    class FlaskApplication(BaseApplication):
        def __init__(self, app):
            self.application = app
            super().__init__()

        def load_config(self):
            self.cfg.set("bind", f"0.0.0.0:{os.environ.get('PORT', 10000)}")

        def load(self):
            return self.application

    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    FlaskApplication(app).run()