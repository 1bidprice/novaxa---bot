import os
import telebot
import logging
from flask import Flask, request

API_TOKEN = '7658672268:AAEHvAKeT9LT5jhk...SZOM'

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Logging setup
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.info(f"[START] {message.from_user.id} - {message.text}")
    bot.reply_to(message, "Καλώς ήρθες στο NOVAXA bot!")

@bot.message_handler(commands=['help'])
def send_help(message):
    logging.info(f"[HELP] {message.from_user.id} - {message.text}")
    bot.reply_to(message,
        "/start - Έναρξη bot\n"
        "/help - Βοήθεια\n"
        "/status - Κατάσταση\n"
        "/getid - Telegram ID\n"
        "/log - Προβολή logs"
    )

@bot.message_handler(commands=['status'])
def send_status(message):
    logging.info(f"[STATUS] {message.from_user.id} - {message.text}")
    bot.reply_to(message, "Το NOVAXA bot είναι online και λειτουργεί κανονικά.")

@bot.message_handler(commands=['getid'])
def send_user_id(message):
    logging.info(f"[GETID] {message.from_user.id} - {message.text}")
    bot.reply_to(message, f"Telegram ID σου: {message.chat.id}")

@bot.message_handler(commands=['log'])
def send_log(message):
    logging.info(f"[LOG] {message.from_user.id} - {message.text}")
    try:
        if os.path.exists("log.txt"):
            with open("log.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()[-30:]
                log_content = "".join(lines)
                if log_content.strip():
                    bot.reply_to(message, f"Τελευταία logs:\n{log_content}")
                else:
                    bot.reply_to(message, "Το log.txt είναι άδειο.")
        else:
            bot.reply_to(message, "Δεν βρέθηκε το αρχείο log.txt.")
    except Exception as e:
        bot.reply_to(message, f"Σφάλμα ανάγνωσης log: {e}")

# Webhook Route
@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# Index για να βλέπεις αν τρέχει
@app.route('/', methods=['GET'])
def index():
    return "NOVAXA bot is running!"

# Main εκκίνηση για Render (webhook binding)
if __name__ == '__main__':
    bot.remove_webhook()
    webhook_url = f"https://novaxa.onrender.com/{API_TOKEN}"
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
