import os
import time
import logging
from flask import Flask
import telebot
from telebot import apihelper
from dotenv import load_dotenv
from threading import Thread

# Load .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Logging setup
logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Rate limit
last_message_time = {}

# Helper: send message with rate limit
def send_limited_message(chat_id, text):
    now = time.time()
    if chat_id not in last_message_time or now - last_message_time[chat_id] > 5:
        bot.send_message(chat_id, text)
        last_message_time[chat_id] = now
    else:
        bot.send_message(chat_id, "⏳ Παρακαλώ περίμενε λίγο πριν ξαναστείλεις εντολή.")

# Commands
@bot.message_handler(commands=["start"])
def start(message):
    send_limited_message(message.chat.id, "Καλώς ήρθες στο NOVAXA bot!")

@bot.message_handler(commands=["help"])
def help_command(message):
    help_text = (
        "📋 Διαθέσιμες εντολές:\n"
        "/start - Έναρξη bot\n"
        "/help - Βοήθεια\n"
        "/getid - Εμφάνιση Chat ID\n"
        "/notify [μήνυμα] - Αποστολή ειδοποίησης\n"
        "/alert [μήνυμα] - Σημαντική ειδοποίηση\n"
        "/broadcast [μήνυμα] - Μαζική ειδοποίηση\n"
        "/status - Κατάσταση bot\n"
        "/log - Προβολή τελευταίων μηνυμάτων"
    )
    send_limited_message(message.chat.id, help_text)

@bot.message_handler(commands=["getid"])
def get_id(message):
    send_limited_message(message.chat.id, f"Το ID σου είναι: {message.chat.id}")

@bot.message_handler(commands=["status"])
def status(message):
    send_limited_message(message.chat.id, "✅ Το bot είναι ενεργό.")

@bot.message_handler(commands=["log"])
def show_logs(message):
    try:
        with open("bot.log", "r") as file:
            lines = file.readlines()[-10:]
            bot.send_message(message.chat.id, "".join(lines) or "Κανένα μήνυμα.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Σφάλμα: {e}")

@bot.message_handler(commands=["notify"])
def notify(message):
    content = message.text.replace("/notify", "").strip()
    if content:
        bot.send_message(message.chat.id, f"🔔 Ειδοποίηση ελήφθη!\n\n{content}")
        logging.info(f"[NOTIFY] {content}")
    else:
        bot.send_message(message.chat.id, "Χρησιμοποίησε την εντολή /notify [μήνυμα].")

@bot.message_handler(commands=["alert"])
def alert(message):
    content = message.text.replace("/alert", "").strip()
    if content:
        bot.send_message(message.chat.id, f"🚨 Σημαντική ειδοποίηση:\n\n{content}")
        logging.info(f"[ALERT] {content}")
    else:
        bot.send_message(message.chat.id, "Χρησιμοποίησε την εντολή /alert [μήνυμα].")

@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    content = message.text.replace("/broadcast", "").strip()
    if content:
        bot.send_message(message.chat.id, f"📢 Ανακοίνωση στάλθηκε!\n\n{content}")
        logging.info(f"[BROADCAST] {content}")
    else:
        bot.send_message(message.chat.id, "Χρησιμοποίησε την εντολή /broadcast [μήνυμα].")

# Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return "NOVAXA bot is running!"

# Auto webhook removal
def remove_webhook():
    try:
        bot.remove_webhook()
        print("Webhook removed.")
    except apihelper.ApiTelegramException as e:
        print("Webhook removal failed:", e)

# Start bot
def run_bot():
    remove_webhook()
    time.sleep(2)
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)