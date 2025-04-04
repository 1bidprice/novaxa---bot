import telebot
import logging
from flask import Flask, request
import os

# --- Ρυθμίσεις Token ---
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- Logging σε αρχείο ---
LOG_FILE = "novaxa.log"
logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()

# --- Flask Webhook App ---
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'NOVAXA is online!', 200

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# --- Εντολές ---
@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f"/start by {message.from_user.id}")
    bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")

@bot.message_handler(commands=['help'])
def help_command(message):
    logger.info(f"/help by {message.from_user.id}")
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/help\n/status\n/log")

@bot.message_handler(commands=['status'])
def status(message):
    logger.info(f"/status by {message.from_user.id}")
    bot.reply_to(message, "Η NOVAXA λειτουργεί κανονικά.")

@bot.message_handler(commands=['log'])
def show_log(message):
    try:
        logger.info(f"/log by {message.from_user.id}")
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            last_lines = ''.join(lines[-10:]) if len(lines) >= 10 else ''.join(lines)
            bot.reply_to(message, f"Τελευταία logs:\n\n{last_lines}")
    except Exception as e:
        bot.reply_to(message, "Σφάλμα κατά την ανάγνωση του αρχείου log.")

# --- Εκκίνηση ---
if __name__ == "__main__":
    import telebot.util
    import requests
    bot.remove_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
