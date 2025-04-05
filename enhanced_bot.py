import telebot
from flask import Flask, request
import time
import os

TOKEN = '7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    return "NOVAXA bot is running.", 200

# Βασικές εντολές bot
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Γεια σου! Το NOVAXA bot είναι ενεργό.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    bot.reply_to(message, "Το NOVAXA bot λειτουργεί κανονικά.")

# Εκκίνηση server + webhook
if __name__ == "__main__":
    time.sleep(2)
    try:
        bot.remove_webhook()
        bot.set_webhook(url=f"https://novaxa.onrender.com/{TOKEN}")
        print("Webhook set successfully.")
    except Exception as e:
        print(f"Error setting webhook: {e}")
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
