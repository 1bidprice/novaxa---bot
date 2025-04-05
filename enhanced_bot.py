import os import telebot import logging from flask import Flask, request

API_TOKEN = '7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM'

bot = telebot.TeleBot(API_TOKEN) app = Flask(name)

Set up logging

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_message(message): user = message.from_user.first_name if message.from_user else 'Unknown' logging.info(f"[{user}] {message.text}")

Telegram commands

@bot.message_handler(commands=['start']) def send_welcome(message): log_message(message) bot.reply_to(message, "Καλώς ήρθες στο NOVAXA Bot!")

@bot.message_handler(commands=['help']) def help_command(message): log_message(message) bot.reply_to(message, "Διαθέσιμες εντολές: /start /help /status /log")

@bot.message_handler(commands=['status']) def status_command(message): log_message(message) bot.reply_to(message, "Το NOVAXA bot είναι online και λειτουργεί κανονικά.")

@bot.message_handler(commands=['log']) def log_command(message): log_message(message) try: if os.path.exists("log.txt"): with open("log.txt", "r") as file: lines = file.readlines()[-10:] bot.reply_to(message, "Τελευταία logs:\n" + "".join(lines)) else: bot.reply_to(message, "Δεν βρέθηκε αρχείο log.txt.") except Exception as e: bot.reply_to(message, f"Σφάλμα κατά την ανάγνωση των logs: {e}")

Webhook route

@app.route(f"/{API_TOKEN}", methods=['POST']) def webhook(): json_string = request.get_data().decode('utf-8') update = telebot.types.Update.de_json(json_string) bot.process_new_updates([update]) return "", 200

@app.route('/', methods=['GET']) def index(): return 'NOVAXA bot is running.', 200

if name == "main": bot.remove_webhook() bot.set_webhook(url=f"https://novaxa.onrender.com/{API_TOKEN}") app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

