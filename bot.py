import telebot
import time
import os
import logging
import threading
import requests
from flask import Flask, request

# === ΡΥΘΜΙΣΕΙΣ ===
TOKEN = "7658672268:AAGZ7QTe5Ra-J7EJfzcIkF8mNZHjDxfqqsg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
log_file = "novaxa.log"
rate_limit_seconds = 5
last_command_time = {}

# === LOGGING ===
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# === RATE LIMIT ===
def is_rate_limited(user_id):
    now = time.time()
    if user_id in last_command_time and now - last_command_time[user_id] < rate_limit_seconds:
        return True
    last_command_time[user_id] = now
    return False

# === ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ===
def log_command(command):
    logging.info(f"Command used: {command}")

def delete_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
    try:
        requests.get(url)
    except Exception as e:
        print(f"Webhook deletion failed: {e}")

# === ΕΝΤΟΛΕΣ BOT ===
@bot.message_handler(commands=['start'])
def start_handler(message):
    if is_rate_limited(message.from_user.id):
        bot.reply_to(message, "⏳ Περιμένετε λίγο πριν δώσετε άλλη εντολή.")
        return
    bot.reply_to(message, "✅ Το bot ξεκίνησε! Χρησιμοποίησε την εντολή /help για οδηγίες.")
    log_command("/start")

@bot.message_handler(commands=['help'])
def help_handler(message):
    help_text = (
        "📌 Διαθέσιμες εντολές:\n"
        "/start - Εκκίνηση bot\n"
        "/help - Εμφάνιση οδηγιών\n"
        "/getid - Εμφάνιση Chat ID\n"
        "/notify <μήνυμα> - Ειδοποίηση μόνο σε εσένα\n"
        "/broadcast <μήνυμα> - Μαζική ειδοποίηση (σε όλους)\n"
        "/alert <μήνυμα> - Ειδοποίηση με emoji\n"
        "/log - Λήψη log αρχείου\n"
        "/status - Κατάσταση bot"
    )
    bot.reply_to(message, help_text)
    log_command("/help")

@bot.message_handler(commands=['getid'])
def getid_handler(message):
    bot.reply_to(message, f"🆔 Το chat ID σου είναι: {message.chat.id}")
    log_command("/getid")

@bot.message_handler(commands=['notify'])
def notify_handler(message):
    if len(message.text.split(' ', 1)) < 2:
        bot.reply_to(message, "Χρήση: /notify <μήνυμα>")
        return
    bot.send_message(message.chat.id, f"🔔 Ειδοποίηση:\n{message.text.split(' ', 1)[1]}")
    log_command("/notify")

@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
    if len(message.text.split(' ', 1)) < 2:
        bot.reply_to(message, "Χρήση: /broadcast <μήνυμα>")
        return
    bot.send_message(message.chat.id, f"📢 ΝΕΑ ΕΙΔΟΠΟΙΗΣΗ:\n{message.text.split(' ', 1)[1]}")
    log_command("/broadcast")

@bot.message_handler(commands=['alert'])
def alert_handler(message):
    if len(message.text.split(' ', 1)) < 2:
        bot.reply_to(message, "Χρήση: /alert <μήνυμα>")
        return
    bot.send_message(message.chat.id, f"⚠️ ALERT:\n{message.text.split(' ', 1)[1]}")
    log_command("/alert")

@bot.message_handler(commands=['log'])
def log_handler(message):
    if os.path.exists(log_file):
        with open(log_file, 'rb') as f:
            bot.send_document(message.chat.id, f)
        log_command("/log")

@bot.message_handler(commands=['status'])
def status_handler(message):
    bot.reply_to(message, "✅ Το bot είναι ενεργό και λειτουργεί κανονικά.")
    log_command("/status")

# === FLASK SERVER ===
@app.route('/')
def index():
    return "NOVAXA bot is running."

# === ΕΝΑΡΞΗ BOT ===
def run_bot():
    delete_webhook()
    time.sleep(2)
    bot.polling(non_stop=True)

def run_server():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    threading.Thread(target=run_server).start()
