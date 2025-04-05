import os
import logging
from flask import Flask, request
import telebot

# === TOKEN ===
API_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(API_TOKEN)

# === Flask App ===
app = Flask(__name__)

# === Logging ===
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# === Webhook Setup ===
WEBHOOK_PATH = f"/{API_TOKEN}"
WEBHOOK_URL = f"https://novaxa.onrender.com{WEBHOOK_PATH}"

@app.route(WEBHOOK_PATH, methods=["POST"])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Unsupported Media Type", 415

# === Bot Commands ===

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Καλωσόρισες στο NOVAXA bot. Είμαι εδώ για να σε βοηθήσω!")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start - Καλωσόρισμα\n/help - Βοήθεια\n/status - Έλεγχος κατάστασης")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "Το NOVAXA bot είναι ενεργό και λειτουργεί κανονικά.")

# === WSGI App Export για Gunicorn ===
if __name__ == "__main__":
    # Χρήση σε τοπικό περιβάλλον μόνο
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    # Χρήση από Gunicorn στο Render
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
