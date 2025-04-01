import telebot
import time
import logging
from flask import Flask
import threading
import os

# ===== CONFIGURATION =====
BOT_TOKEN = os.environ.get("TOKEN")  # Από το Render Dashboard (Environment Variables)
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ===== LOGGING =====
logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# ===== RATE LIMIT =====
user_last_message_time = {}
rate_limit_seconds = 3  # Όριο ανά χρήστη (σε δευτερόλεπτα)

def is_rate_limited(user_id):
    current_time = time.time()
    if user_id in user_last_message_time:
        if current_time - user_last_message_time[user_id] < rate_limit_seconds:
            return True
    user_last_message_time[user_id] = current_time
    return False

# ===== BASIC COMMANDS =====
@bot.message_handler(commands=['start'])
def start(message):
    if is_rate_limited(message.from_user.id):
        return
    bot.reply_to(message, "Καλώς ήρθες στο NOVAXA Bot! Στείλε /help για οδηγίες.")

@bot.message_handler(commands=['help'])
def help_command(message):
    if is_rate_limited(message.from_user.id):
        return
    help_text = (
        "Διαθέσιμες εντολές:\n"
        "/start - Έναρξη\n"
        "/help - Οδηγίες\n"
        "/status - Έλεγχος κατάστασης\n"
        "/getid - Λήψη Telegram ID\n"
        "/notify <μήνυμα> - Αποστολή ειδοποίησης στον εαυτό σου\n"
        "/alert <μήνυμα> - Alert με ping\n"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['status'])
def status(message):
    if is_rate_limited(message.from_user.id):
        return
    bot.reply_to(message, "Το NOVAXA bot λειτουργεί κανονικά!")

@bot.message_handler(commands=['getid'])
def getid(message):
    if is_rate_limited(message.from_user.id):
        return
    user_id = message.from_user.id
    bot.reply_to(message, f"Το Telegram ID σου είναι: {user_id}")

@bot.message_handler(commands=['notify'])
def notify(message):
    if is_rate_limited(message.from_user.id):
        return
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        bot.reply_to(message, "Χρήση: /notify <μήνυμα>")
    else:
        bot.send_message(message.chat.id, f"Ειδοποίηση: {text[1]}")

@bot.message_handler(commands=['alert'])
def alert(message):
    if is_rate_limited(message.from_user.id):
        return
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        bot.reply_to(message, "Χρήση: /alert <μήνυμα>")
    else:
        bot.send_message(message.chat.id, f"🔔 ALERT: {text[1]}")

# ===== FLASK ROUTE (αν χρειαστεί στο μέλλον για webhook) =====
@app.route('/')
def index():
    return "NOVAXA bot is running!"

# ===== BOT THREAD =====
def run_bot():
    try:
        bot.polling(non_stop=True, interval=0)
    except Exception as e:
        logging.error(f"Bot crashed: {e}")

# ===== START =====
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)