import os
import telebot
from flask import Flask, request

# === Ρυθμίσεις ===
BOT_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
WEBHOOK_URL = f"https://novaxa.onrender.com/{BOT_TOKEN}"
LOG_FILE = "log.txt"

# === Bot & Flask ===
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === Logging ===
def log(entry):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{entry}\n")

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== NOVAXA LOG START ===\n")

# === Routes ===
@app.route('/', methods=['GET'])
def home():
    return 'NOVAXA v2.0 is running!'

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.data.decode('utf-8'))
        bot.process_new_updates([update])
    except Exception as e:
        log(f"Webhook error: {e}")
    return '', 200

# === Commands ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")
    log(f"{message.from_user.first_name} used /start")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/help\n/status\n/log")
    log(f"{message.from_user.first_name} used /help")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "Η NOVAXA λειτουργεί κανονικά.")
    log(f"{message.from_user.first_name} used /status")

@bot.message_handler(commands=['log'])
def show_log(message):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        bot.reply_to(message, content[-4000:] if len(content) > 4000 else content)
        log(f"{message.from_user.first_name} used /log")
    except Exception as e:
        bot.reply_to(message, "Σφάλμα ανάγνωσης log.")
        log(f"Log read error: {e}")

# === Εκκίνηση ===
if __name__ == '__main__':
    import telebot.apihelper
    try:
        bot.remove_webhook()
    except:
        pass

    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
