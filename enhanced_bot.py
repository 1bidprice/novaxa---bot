import os
import logging
from flask import Flask, request
import telebot

API_TOKEN = "7658672268:AAEHvAKeT9LT5jhk..."
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# === Logging ===
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# === Webhook route ===
@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# === Commands ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Καλωσόρισες στο NOVAXA bot!")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "Το bot είναι ενεργό και λειτουργεί σωστά.")

# === App binding ===
if __name__ == "__main__":
    # Optional webhook deletion logic here if needed
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
