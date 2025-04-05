import os
import telebot
import logging
from flask import Flask, request

API_TOKEN = '7658672268:AAEHvAKeT9LT5jhk...SZOM'  # απόκρυψε δημόσια

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# === Start command ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.info(f"[START] {message.from_user.id} - {message.text}")
    bot.reply_to(message, "Καλώς ήρθες στο NOVAXA bot!")

# === Help command ===
@bot.message_handler(commands=['help'])
def send_help(message):
    logging.info(f"[HELP] {message.from_user.id} - {message.text}")
    bot.reply_to(message,
        "/start - Έναρξη bot\n"
        "/help - Βοήθεια\n"
        "/status - Κατάσταση\n"
        "/getid - Εμφάνιση Telegram ID\n"
        "/log - Εμφάνιση αρχείου log"
    )

# === Status command ===
@bot.message_handler(commands=['status'])
def send_status(message):
    logging.info(f"[STATUS] {message.from_user.id} - {message.text}")
    bot.reply_to(message, "Το NOVAXA bot είναι online και λειτουργεί κανονικά.")

# === Get Telegram ID ===
@bot.message_handler(commands=['getid'])
def send_user_id(message):
    logging.info(f"[GETID] {message.from_user.id} - {message.text}")
    bot.reply_to(message, f"Telegram ID σου: {message.chat.id}")

# === Log command ===
@bot.message_handler(commands=['log'])
def send_log(message):
    logging.info(f"[LOG] {message.from_user.id} - {message.text}")
    try:
        if os.path.exists("log.txt"):
            with open("log.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()[-30:]
            log_content = "".join(lines)
            if log_content.strip():
                bot.reply_to(message, f"Τελευταία logs:\n{log_content}")
            else:
                bot.reply_to(message, "Το αρχείο log.txt είναι άδειο.")
        else:
            bot.reply_to(message, "Δεν βρέθηκε το αρχείο log.txt.")
    except Exception as e:
        bot.reply_to(message, f"Σφάλμα κατά την ανάγνωση logs: {e}")

# === Webhook route ===
@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

# === Index ===
@app.route("/", methods=['GET'])
def index():
    return "NOVAXA bot is running!"

# === Main entrypoint ===
if __name__ == "__main__":
    webhook_url = f"https://novaxa.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))