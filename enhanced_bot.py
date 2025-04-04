import os import telebot from flask import Flask, request

API_TOKEN = '7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM' bot = telebot.TeleBot(API_TOKEN)

app = Flask(name)

Handlers

@bot.message_handler(commands=['start']) def send_welcome(message): bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")

@bot.message_handler(commands=['help']) def help_message(message): bot.reply_to(message, "Διαθέσιμες εντολές: /start /help /status /log /getid")

@bot.message_handler(commands=['status']) def status(message): bot.reply_to(message, "Η NOVAXA λειτουργεί κανονικά.")

@bot.message_handler(commands=['getid']) def get_id(message): bot.reply_to(message, f"Το ID σου είναι: {message.chat.id}")

@bot.message_handler(commands=['log']) def get_log(message): bot.reply_to(message, "[Λειτουργία log υπό κατασκευή]")

Webhook route

@app.route(f"/{API_TOKEN}", methods=['POST']) def receive_update(): json_str = request.get_data().decode("utf-8") update = telebot.types.Update.de_json(json_str) bot.process_new_updates([update]) return "", 200

Root route

@app.route("/") def index(): return "NOVAXA v2.0 is live!"

Start app

if name == "main": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

