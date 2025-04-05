import os
import telebot
from flask import Flask, request

TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Καλωσήρθες στο NOVAXA bot!")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/help\n/status\n/getid\n/log")

@bot.message_handler(commands=['status'])
def send_status(message):
    bot.reply_to(message, "Το bot είναι ενεργό και λειτουργεί κανονικά.")

@bot.message_handler(commands=['getid'])
def send_user_id(message):
    bot.reply_to(message, f"Το Telegram ID σου είναι: {message.chat.id}")

@bot.message_handler(commands=['log'])
def send_log(message):
    if os.path.exists("log.txt"):
        with open("log.txt", "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()[-30:]
            log_content = "".join(lines)
            if log_content.strip():
                bot.reply_to(message, f"Τελευταία logs:\n\n{log_content}")
            else:
                bot.reply_to(message, "Το αρχείο log.txt είναι άδειο.")
    else:
        bot.reply_to(message, "Δεν βρέθηκε αρχείο log.txt στο σύστημα.")

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return "NOVAXA bot is running!"

if __name__ == '__main__':
    webhook_url = f"https://novaxa.onrender.com/{TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
