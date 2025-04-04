import os
import telebot
from flask import Flask, request

# Telegram Bot Token (ενσωματωμένο απευθείας στον κώδικα)
BOT_TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"
bot = telebot.TeleBot(BOT_TOKEN)

# Δημιουργία log.txt αν δεν υπάρχει
if not os.path.exists("log.txt"):
    with open("log.txt", "w", encoding="utf-8") as f:
        f.write("=== NOVAXA LOG START ===\n")

# Flask App για webhook
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "NOVAXA v2.0 is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# Εντολές Telegram
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user.first_name
    bot.reply_to(message, "Καλωσήρθες στη NOVAXA v2.0!")
    log(f"{user} used /start")

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
        with open("log.txt", "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 4000:
            content = content[-4000:]
        bot.reply_to(message, f"Log αρχείο:\n\n{content}")
        log(f"{message.from_user.first_name} used /log")
    except Exception as e:
        bot.reply_to(message, "Σφάλμα κατά την ανάγνωση του log.")
        log(f"ERROR reading log: {e}")

# Συνάρτηση καταγραφής
def log(entry):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{entry}\n")

# Εκκίνηση εφαρμογής Flask
if __name__ == '__main__':
    import telebot.apihelper
    try:
        bot.delete_webhook()
    except Exception:
        pass
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
