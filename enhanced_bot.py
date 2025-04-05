import telebot
import logging
import requests
from flask import Flask

TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# LOGGING
logging.basicConfig(level=logging.INFO)

# HANDLERS
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Καλωσήρθες στο NOVAXA bot!")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, "Χρησιμοποίησε τις εντολές: /start, /status, /log")

@bot.message_handler(commands=['status'])
def handle_status(message):
    bot.reply_to(message, "Το bot είναι ενεργό και λειτουργεί κανονικά.")

# ROUTE για να ενεργοποιηθεί το webhook
@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://novaxa.onrender.com/{TOKEN}"
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        data={"url": webhook_url}
    )
    if response.status_code == 200:
        return "Webhook set successfully!"
    else:
        return f"Webhook failed: {response.text}"

# ROUTE για να δέχεται τα updates
@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    try:
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    except Exception as e:
        logging.error(f"Error processing update: {e}")
    return "OK"

# FLASK APP
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
