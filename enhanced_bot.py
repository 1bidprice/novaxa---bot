import os
import telebot
from flask import Flask, request

# === TOKEN (απευθείας ενσωματωμένο) ===
BOT_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(BOT_TOKEN)

# === Flask App για Webhook ===
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "NOVAXA v2.0 is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# === Εντολές Bot ===
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/help\n/status\n/log")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    bot.reply_to(message, "Η NOVAXA λειτουργεί κανονικά.")

@bot.message_handler(commands=['log'])
def log_cmd(message):
    try:
        with open("log.txt", "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 4000:
            content = content[-4000:]
        bot.reply_to(message, f"Log αρχείο:\n\n{content}")
    except Exception:
        bot.reply_to(message, "Δεν βρέθηκε αρχείο log.")

# === Εκκίνηση (ΜΟΝΟ για Render/Gunicorn) ===
if __name__ != "__main__":
    import telebot.apihelper
    try:
        bot.remove_webhook()
    except Exception:
        pass

    # Ορισμός webhook (μόνο τη 1η φορά ή αν αλλάξει το URL)
    WEBHOOK_URL = f"https://novaxa.onrender.com/{BOT_TOKEN}"
    bot.set_webhook(url=WEBHOOK_URL)

    # Δημιουργία log.txt αν δεν υπάρχει
    if not os.path.exists("log.txt"):
        with open("log.txt", "w", encoding="utf-8") as f:
            f.write("=== NOVAXA LOG START ===\n")
