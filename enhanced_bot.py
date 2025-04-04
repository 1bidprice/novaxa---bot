import telebot
import logging
import os
from flask import Flask, request

# Token από τα Environment Variables
TOKEN = os.environ.get("TOKEN")

# Δημιουργία bot
bot = telebot.TeleBot(TOKEN)

# Flask App
app = Flask(__name__)

# Logging για debugging
logging.basicConfig(level=logging.INFO)

# === ROUTES ===
@app.route('/', methods=['GET'])
def index():
    return 'NOVAXA v2.0 online'

@app.route('/' + TOKEN, methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

# === HANDLERS ===
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/help\n/status")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    bot.reply_to(message, "Η NOVAXA λειτουργεί κανονικά.")

# === MAIN ===
if __name__ == '__main__':
    # Διαγραφή webhook πρώτα για να αποφευχθεί conflict
    bot.remove_webhook()

    # Ρύθμιση νέου webhook στη διεύθυνση Render
    bot.set_webhook(url='https://novaxa.onrender.com/' + TOKEN)

    # Εκκίνηση Flask με σωστό binding για Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
