import telebot
from flask import Flask, request
import os
import logging

# === CONFIG ===
TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ROUTES ===
@app.route('/', methods=['GET'])
def home():
    return 'NOVAXA Bot is Live!', 200

@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# === HANDLERS ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Καλωσήρθες στη NOVAXA v2.0!")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Διαθέσιμες εντολές: /start, /help, /status, /getid")

@bot.message_handler(commands=['status'])
def handle_status(message):
    bot.send_message(message.chat.id, "Η NOVAXA λειτουργεί κανονικά.")

@bot.message_handler(commands=['getid'])
def handle_getid(message):
    bot.send_message(message.chat.id, f"Το Telegram ID σου είναι: {message.chat.id}")

# === MAIN ===
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
