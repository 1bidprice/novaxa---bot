import os
import logging
from flask import Flask, request
import telebot

API_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# === Logging ===
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# === Telegram Commands ===

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.info(f"[START] {message.from_user.id} - {message.text}")
    bot.reply_to(message, "ΞΞ±Ξ»ΟΟ Ξ�ΟΞΈΞ΅Ο ΟΟΞΏ NOVAXA bot!")

@bot.message_handler(commands=['help'])
def send_help(message):
    logging.info(f"[HELP] {message.from_user.id} - {message.text}")
    bot.reply_to(message, "/start - ΞΞ½Ξ±ΟΞΎΞ·
/help - ΞΞΏΞ�ΞΈΞ΅ΞΉΞ±
/status - ΞΞ±ΟΞ¬ΟΟΞ±ΟΞ·
/getid - Ξ€ΞΏ ID ΟΞΏΟ
/log - Ξ€Ξ΅Ξ»Ξ΅ΟΟΞ±Ξ―Ξ± logs")

@bot.message_handler(commands=['status'])
def send_status(message):
    logging.info(f"[STATUS] {message.from_user.id} - {message.text}")
    bot.reply_to(message, "Ξ€ΞΏ NOVAXA bot Ξ΅Ξ―Ξ½Ξ±ΞΉ online ΞΊΞ±ΞΉ Ξ»Ξ΅ΞΉΟΞΏΟΟΞ³Ξ΅Ξ― ΟΟΟΟΞ¬.")

@bot.message_handler(commands=['getid'])
def send_user_id(message):
    logging.info(f"[GETID] {message.from_user.id} - {message.text}")
    bot.reply_to(message, f"Ξ€ΞΏ Telegram ID ΟΞΏΟ Ξ΅Ξ―Ξ½Ξ±ΞΉ: {message.chat.id}")

@bot.message_handler(commands=['log'])
def send_log(message):
    try:
        if os.path.exists("log.txt"):
            with open("log.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()[-30:]
            log_content = "".join(lines)
            if log_content.strip():
                bot.reply_to(message, f"Ξ€Ξ΅Ξ»Ξ΅ΟΟΞ±Ξ―Ξ± logs:
{log_content}")
            else:
                bot.reply_to(message, "Ξ€ΞΏ Ξ±ΟΟΞ΅Ξ―ΞΏ log.txt Ξ΅Ξ―Ξ½Ξ±ΞΉ Ξ¬Ξ΄Ξ΅ΞΉΞΏ.")
        else:
            bot.reply_to(message, "ΞΞ΅Ξ½ ΟΟΞ¬ΟΟΞ΅ΞΉ Ξ±ΟΟΞ΅Ξ―ΞΏ log.txt.")
    except Exception as e:
        bot.reply_to(message, f"Ξ£ΟΞ¬Ξ»ΞΌΞ± ΞΊΞ±ΟΞ¬ ΟΞ·Ξ½ Ξ±Ξ½Ξ¬Ξ³Ξ½ΟΟΞ· log: {e}")

# === Flask Webhook ===

@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return "NOVAXA bot is running!"

if __name__ == '__main__':
    webhook_url = f"https://novaxa.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
