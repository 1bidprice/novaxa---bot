import telebot
import requests
import logging

# Ρύθμιση TOKEN (αντικατέστησέ το με το δικό σου)
TOKEN = '7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM'
bot = telebot.TeleBot(TOKEN)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Εντολές bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Καλώς ήρθες στο NOVAXA v2.0")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "Το NOVAXA bot λειτουργεί κανονικά.\n\nΚατάσταση έργων:\n\nBidPrice (Active) - Πρόοδος: 75%\nAmesis (In Development) - Πρόοδος: 60%")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "Διαθέσιμες εντολές:\n/start\n/status\n/help\n/getid")

@bot.message_handler(commands=['getid'])
def get_id(message):
    bot.reply_to(message, f"Το Telegram ID σου είναι: {message.chat.id}")

# Κύρια εκκίνηση
if __name__ == '__main__':
    # Διαγραφή υπάρχοντος webhook για αποφυγή σφάλματος 409
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
        logging.info("Webhook deleted successfully.")
    except Exception as e:
        logging.warning(f"Failed to delete webhook: {e}")

    # Εκκίνηση bot με polling
    bot.polling(non_stop=True, long_polling_timeout=30)
