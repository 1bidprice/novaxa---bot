
import telebot
from flask import Flask
import time
import logging
from threading import Thread

# === TOKEN (ενσωματωμένο) ===
API_TOKEN = '7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM'

# === Ρύθμιση Logging ===
logging.basicConfig(
    filename='bot_log.txt',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# === Αρχικοποίηση bot και Flask ===
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
rate_limit = {}

# === Rate limit decorator ===
def limited(func):
    def wrapper(message):
        user_id = message.chat.id
        current_time = time.time()
        if user_id in rate_limit and current_time - rate_limit[user_id] < 3:
            bot.send_message(user_id, "Περίμενε λίγο πριν ξαναδοκιμάσεις.")
            return
        rate_limit[user_id] = current_time
        func(message)
    return wrapper

# === /start ===
@bot.message_handler(commands=['start'])
@limited
def send_welcome(message):
    bot.reply_to(message, "Καλωσόρισες στο NOVAXA bot!")

# === /help ===
@bot.message_handler(commands=['help'])
@limited
def help_command(message):
    help_text = (
        "/start - Εκκίνηση bot\n"
        "/help - Εμφάνιση διαθέσιμων εντολών\n"
        "/status - Έλεγχος λειτουργίας bot\n"
        "/getid - Επιστροφή του Telegram ID\n"
        "/notify - Αποστολή ειδοποίησης\n"
        "/broadcast - Μαζική αποστολή σε χρήστες\n"
        "/alert - Alert μήνυμα\n"
        "/log - Έλεγχος καταγραφών bot"
    )
    bot.send_message(message.chat.id, help_text)

# === /status ===
@bot.message_handler(commands=['status'])
@limited
def status(message):
    bot.reply_to(message, "Το NOVAXA bot λειτουργεί κανονικά.")

# === /getid ===
@bot.message_handler(commands=['getid'])
@limited
def getid(message):
    bot.reply_to(message, f"Το ID σου είναι: {message.chat.id}")

# === /notify ===
@bot.message_handler(commands=['notify'])
@limited
def notify(message):
    bot.reply_to(message, "Η ειδοποίηση στάλθηκε.")

# === /broadcast ===
@bot.message_handler(commands=['broadcast'])
@limited
def broadcast(message):
    bot.reply_to(message, "Η μαζική αποστολή ενεργοποιήθηκε.")

# === /alert ===
@bot.message_handler(commands=['alert'])
@limited
def alert(message):
    bot.reply_to(message, "Alert! Ενεργοποιήθηκε ειδοποίηση.")

# === /log ===
@bot.message_handler(commands=['log'])
@limited
def send_log(message):
    try:
        with open('bot_log.txt', 'r') as f:
            lines = f.readlines()[-15:]  # Τελευταίες 15 γραμμές
            bot.send_message(message.chat.id, ''.join(lines) or "Κενό log.")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Δεν βρέθηκε αρχείο log.")

# === Flask route για webhook ===
@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    time.sleep(1)
    return 'Webhook cleared. Bot λειτουργεί με polling.'

# === Εκκίνηση polling σε thread ===
def run_bot():
    try:
        bot.remove_webhook()
        time.sleep(1)
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Polling error: {e}")

# === Εκκίνηση Flask και bot ===
if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)