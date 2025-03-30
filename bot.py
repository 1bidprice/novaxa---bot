import telebot
import time
import os
import logging
import threading
import requests
from flask import Flask, request
from dotenv import load_dotenv

# === ΑΡΧΙΚΗ ΡΥΘΜΙΣΗ ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
log_file = "novaxa.log"
limit_seconds = 5
last_command_time = {}

# === ΜΗΧΑΝΙΣΜΟΣ RATE LIMIT ===
def is_allowed(user_id):
    now = time.time()
    last_time = last_command_time.get(user_id, 0)
    if now - last_time >= limit_seconds:
        last_command_time[user_id] = now
        return True
    return False

# === ΚΑΤΑΓΡΑΦΗ ΕΝΤΟΛΩΝ ===
def log_command(command):
    with open(log_file, "a") as file:
        file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {command}\n")

# === ΕΝΤΟΛΕΣ BOT ===
@bot.message_handler(commands=['start'])
def start(message):
    if is_allowed(message.from_user.id):
        bot.reply_to(message, "Καλώς ήρθες στο NOVAXA bot!")
        log_command("/start")

@bot.message_handler(commands=['help'])
def help(message):
    if is_allowed(message.from_user.id):
        bot.reply_to(message, "Χρησιμοποίησε την εντολή / για οδηγίες.")
        log_command("/help")

@bot.message_handler(commands=['status'])
def status(message):
    if is_allowed(message.from_user.id):
        bot.reply_to(message, "✅ Το bot είναι ενεργό.")
        log_command("/status")

@bot.message_handler(commands=['getid'])
def getid(message):
    if is_allowed(message.from_user.id):
        bot.reply_to(message, f"Το ID σου είναι: {message.from_user.id}")
        log_command("/getid")

@bot.message_handler(commands=['notify'])
def notify(message):
    if is_allowed(message.from_user.id):
        bot.send_message(message.chat.id, "🔔 Ειδοποίηση ελήφθη!")
        log_command("/notify")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if is_allowed(message.from_user.id):
        bot.send_message(message.chat.id, "📣 Ανακοίνωση στάλθηκε!")
        log_command("/broadcast")

@bot.message_handler(commands=['alert'])
def alert(message):
    if is_allowed(message.from_user.id):
        bot.send_message(message.chat.id, "⚠️ Συναγερμός ενεργοποιήθηκε!")
        log_command("/alert")

@bot.message_handler(commands=['log'])
def send_log(message):
    if os.path.exists(log_file):
        with open(log_file, 'rb') as f:
            bot.send_document(message.chat.id, f)
        log_command("/log")

# === FLASK SERVER ===
@app.route('/')
def index():
    return "NOVAXA bot is running."

# === ΕΝΑΡΞΗ BOT ===
def run_bot():
    bot.delete_webhook()
    time.sleep(2)
    bot.polling(non_stop=True)

def run_server():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    threading.Thread(target=run_server).start()
