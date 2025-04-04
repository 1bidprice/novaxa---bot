import os
import telebot
from flask import Flask, request

BOT_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "NOVAXA v2.0 is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid Content-Type', 403

# HANDLERS

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "Η NOVAXA λειτουργεί κανονικά.")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/status\n/help")

@bot.message_handler(commands=['getid'])
def getid(message):
    bot.reply_to(message, f"Το ID σου είναι: {message.from_user.id}")

# MAIN

if __name__ == '__main__':
    import telebot.apihelper
    try:
        bot.delete_webhook()
    except Exception:
        pass

    # Set webhook
    webhook_url = f"https://novaxa.onrender.com/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
