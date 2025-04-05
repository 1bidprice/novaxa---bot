import os
import logging
from flask import Flask, request
import telebot

API_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# === Logging ===
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# === Set Webhook Route ===
@app.route('/setwebhook')
def set_webhook():
    webhook_url = f"https://novaxa.onrender.com/{API_TOKEN}"
    result = bot.set_webhook(url=webhook_url)
    return "Webhook set: " + str(result)

# === Webhook Receiver ===
@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# === Bot Commands ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Γεια σου! Το bot είναι ενεργό.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, "Διαθέσιμες εντολές: /start, /help, /status")

@bot.message_handler(commands=['status'])
def handle_status(message):
    bot.reply_to(message, "✅ Το bot λειτουργεί κανονικά.")

# === Flask App Entry Point ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
