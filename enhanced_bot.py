import os
import telebot
from flask import Flask, request

# === CONFIG ===
BOT_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === CREATE LOG FILE IF NOT EXISTS ===
LOG_FILE = "log.txt"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== NOVAXA LOG START ===\n")

# === TELEGRAM COMMAND HANDLERS ===
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")
    log(f"{message.from_user.first_name} used /start")

@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/help\n/status\n/log")
    log(f"{message.from_user.first_name} used /help")

@bot.message_handler(commands=["status"])
def handle_status(message):
    bot.reply_to(message, "Η NOVAXA λειτουργεί κανονικά.")
    log(f"{message.from_user.first_name} used /status")

@bot.message_handler(commands=["log"])
def handle_log(message):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 4000:
            content = content[-4000:]
        bot.reply_to(message, f"Log αρχείο:\n\n{content}")
        log(f"{message.from_user.first_name} used /log")
    except Exception as e:
        bot.reply_to(message, "Σφάλμα κατά την ανάγνωση του log.")
        log(f"ERROR reading log: {e}")

# === LOGGING FUNCTION ===
def log(entry):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{entry}\n")

# === FLASK ROUTES ===
@app.route("/", methods=["GET"])
def index():
    return "NOVAXA v2.0 is running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

# === APP START (GUNICORN + WEBHOOK SUPPORT) ===
if __name__ == "__main__":
    try:
        bot.remove_webhook()
    except Exception:
        pass

    webhook_url = f"https://novaxa.onrender.com/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
