import os
import telebot
from flask import Flask, request

# === Token Bot ===
BOT_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(BOT_TOKEN)

# === Δημιουργία αρχείου log.txt αν δεν υπάρχει ===
if not os.path.exists("log.txt"):
    with open("log.txt", "w", encoding="utf-8") as f:
        f.write("=== NOVAXA LOG START ===\n")

# === Flask App ===
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "NOVAXA v2.0 Webhook Running"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# === Commands ===
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")
    log(f"{message.from_user.first_name} used /start")

@bot.message_handler(commands=["help"])
def help_cmd(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/help\n/status\n/log")
    log(f"{message.from_user.first_name} used /help")

@bot.message_handler(commands=["status"])
def status(message):
    bot.reply_to(message, "Η NOVAXA λειτουργεί κανονικά.")
    log(f"{message.from_user.first_name} used /status")

@bot.message_handler(commands=["log"])
def show_log(message):
    try:
        with open("log.txt", "r", encoding="utf-8") as f:
            content = f.read()[-4000:]
        bot.reply_to(message, f"Log αρχείο:\n\n{content}")
        log(f"{message.from_user.first_name} used /log")
    except Exception as e:
        bot.reply_to(message, "Σφάλμα κατά την ανάγνωση του log.")
        log(f"ERROR reading log: {e}")

# === Συνάρτηση Καταγραφής ===
def log(entry):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{entry}\n")

# === Ενεργοποίηση Webhook ===
if __name__ == "__main__":
    try:
        bot.remove_webhook()
    except Exception:
        pass

    webhook_url = f"https://novaxa.onrender.com/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
