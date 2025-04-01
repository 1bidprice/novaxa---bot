import telebot from flask import Flask import time import logging import threading

API_TOKEN = '7658672268:AAHjzU-RICSnT44JKOJyAW1YPhrglUZBTHk' bot = telebot.TeleBot(API_TOKEN)

Rate limit dictionary

user_last_message = {} rate_limit_seconds = 5

Logging setup

logging.basicConfig(filename='bot_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def rate_limited(message): user_id = message.from_user.id now = time.time() if user_id in user_last_message and now - user_last_message[user_id] < rate_limit_seconds: return True user_last_message[user_id] = now return False

@bot.message_handler(commands=['start']) def send_welcome(message): if rate_limited(message): return bot.reply_to(message, "Καλώς ήρθες στο NOVAXA bot!")

@bot.message_handler(commands=['help']) def help_message(message): if rate_limited(message): return bot.reply_to(message, "/start - Έναρξη bot\n/help - Βοήθεια\n/status - Έλεγχος κατάστασης\n/getid - Το ID σου\n/notify - Μήνυμα μόνο σε εσένα\n/broadcast - Μαζικό μήνυμα\n/alert - Συναγερμός\n/log - Τελευταία logs")

@bot.message_handler(commands=['status']) def status(message): if rate_limited(message): return bot.reply_to(message, "Το bot είναι ενεργό και λειτουργεί σωστά.")

@bot.message_handler(commands=['getid']) def get_user_id(message): if rate_limited(message): return bot.reply_to(message, f"Το ID σου είναι: {message.from_user.id}")

@bot.message_handler(commands=['notify']) def notify(message): if rate_limited(message): return text = message.text.split(' ', 1) if len(text) > 1: bot.send_message(message.chat.id, text[1]) else: bot.reply_to(message, "Χρησιμοποίησε: /notify [μήνυμα]")

@bot.message_handler(commands=['broadcast']) def broadcast(message): if rate_limited(message): return if message.from_user.id != 6156148301: bot.reply_to(message, "Δεν έχεις άδεια για αυτήν την εντολή.") return text = message.text.split(' ', 1) if len(text) < 2: bot.reply_to(message, "Χρήση: /broadcast [μήνυμα]") return with open('users.txt', 'r') as f: for line in f: try: bot.send_message(int(line.strip()), text[1]) except: continue

@bot.message_handler(commands=['alert']) def alert(message): if rate_limited(message): return bot.send_message(message.chat.id, "** ALERT ** - Έκτακτη ειδοποίηση!")

@bot.message_handler(commands=['log']) def send_log(message): if rate_limited(message): return try: with open("bot_log.txt", "r") as f: lines = f.readlines()[-10:] bot.reply_to(message, ''.join(lines)) except: bot.reply_to(message, "Δεν βρέθηκε αρχείο log.")

@bot.message_handler(func=lambda message: True) def echo_all(message): if rate_limited(message): return logging.info(f"{message.from_user.id}: {message.text}") with open("users.txt", "a") as f: f.write(f"{message.chat.id}\n")

Flask setup

app = Flask(name)

@app.route('/') def index(): return 'NOVAXA bot is running!'

def run_polling(): time.sleep(5) try: bot.delete_webhook() except: pass bot.infinity_polling()

if name == 'main': threading.Thread(target=run_polling).start() app.run(host='0.0.0.0', port=10000)

