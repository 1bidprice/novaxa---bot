import telebot
from flask import Flask, request
import os

API_TOKEN = '7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM'  # ΤΟ ΚΑΙΝΟΥΡΙΟ TOKEN
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Webhook route
@app.route('/setwebhook')
def set_webhook():
    webhook_url = f'https://novaxa.onrender.com/{API_TOKEN}'
    if bot.remove_webhook():
        bot.set_webhook(url=webhook_url)
        return 'Webhook set successfully!'
    return 'Failed to set webhook.'

# Webhook handler route
@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return '', 403

# /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Καλώς ήρθες στο BidPriceBot!")

# /help command (προαιρετικά ενεργοποιημένο)
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Διαθέσιμες εντολές: /start, /help")

# Flask app binding
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)