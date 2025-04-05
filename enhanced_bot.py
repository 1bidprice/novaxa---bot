import telebot
from flask import Flask, request
import os

API_TOKEN = '7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM'

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# ====== Telegram Commands ======

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Καλώς ήρθες στο NOVAXA Bot!")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Διαθέσιμες εντολές: /start /help /status")

@bot.message_handler(commands=['status'])
def send_status(message):
    bot.reply_to(message, "Το bot είναι ενεργό και λειτουργεί κανονικά!")

# ====== Webhook Endpoint ======

@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://novaxa.onrender.com/{API_TOKEN}"
    if bot.set_webhook(url=webhook_url):
        return "Webhook set successfully!"
    else:
        return "Webhook setup failed!"

@app.route('/', methods=['GET'])
def index():
    return "NOVAXA bot is running!", 200

# ====== Gunicorn Entry Point ======

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
