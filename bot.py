

import telebot
import time
import requests
import logging
from flask import Flask
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Setup
API_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Logging
logging.basicConfig(filename="bot.log", level=logging.INFO)

# Rate limit
last_command_time = {}

def rate_limited(user_id, limit=3):
    now = time.time()
    if user_id in last_command_time and now - last_command_time[user_id] < limit:
        return True
    last_command_time[user_id] = now
    return False

# ===== Command Handlers =====

@bot.message_handler(commands=['start'])
def start_command(message):
    if rate_limited(message.chat.id): return
    bot.reply_to(message, "ΞΞ±Ξ»ΟΟ Ξ�ΟΞΈΞ΅Ο ΟΟΞΏ NOVAXA bot!")

@bot.message_handler(commands=['help'])
def help_command(message):
    if rate_limited(message.chat.id): return
    help_text = ("π ΞΞΉΞ±ΞΈΞ­ΟΞΉΞΌΞ΅Ο Ξ΅Ξ½ΟΞΏΞ»Ξ­Ο:
"
                 "/start - ΞΞ½Ξ±ΟΞΎΞ· bot
"
                 "/help - ΞΞΏΞ�ΞΈΞ΅ΞΉΞ±
"
                 "/getid - ΞΞΌΟΞ¬Ξ½ΞΉΟΞ· Chat ID
"
                 "/notify [ΞΌΞ�Ξ½ΟΞΌΞ±] - ΞΟΞΏΟΟΞΏΞ»Ξ� Ξ΅ΞΉΞ΄ΞΏΟΞΏΞ―Ξ·ΟΞ·Ο
"
                 "/alert [ΞΌΞ�Ξ½ΟΞΌΞ±] - Ξ£Ξ·ΞΌΞ±Ξ½ΟΞΉΞΊΞ� Ξ΅ΞΉΞ΄ΞΏΟΞΏΞ―Ξ·ΟΞ·
"
                 "/broadcast [ΞΌΞ�Ξ½ΟΞΌΞ±] - ΞΞ±ΞΆΞΉΞΊΞ� Ξ΅ΞΉΞ΄ΞΏΟΞΏΞ―Ξ·ΟΞ·
"
                 "/status - ΞΞ±ΟΞ¬ΟΟΞ±ΟΞ· bot
"
                 "/log - Ξ ΟΞΏΞ²ΞΏΞ»Ξ� ΟΞ΅Ξ»Ξ΅ΟΟΞ±Ξ―ΟΞ½ ΞΌΞ·Ξ½ΟΞΌΞ¬ΟΟΞ½")
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['getid'])
def getid_command(message):
    if rate_limited(message.chat.id): return
    bot.reply_to(message, f"Ξ€ΞΏ ID ΟΞΏΟ Ξ΅Ξ―Ξ½Ξ±ΞΉ: {message.chat.id}")

@bot.message_handler(commands=['status'])
def status_command(message):
    if rate_limited(message.chat.id): return
    bot.reply_to(message, "β Ξ€ΞΏ bot Ξ΅Ξ―Ξ½Ξ±ΞΉ Ξ΅Ξ½Ξ΅ΟΞ³Ο.")

@bot.message_handler(commands=['notify'])
def notify_command(message):
    if rate_limited(message.chat.id): return
    text = message.text.replace("/notify", "").strip()
    if text:
        bot.reply_to(message, "π ΞΞΉΞ΄ΞΏΟΞΏΞ―Ξ·ΟΞ· Ξ΅Ξ»Ξ�ΟΞΈΞ·!")
    else:
        bot.reply_to(message, "β Ξ Ξ±ΟΞ±ΞΊΞ±Ξ»Ο Ξ³ΟΞ¬ΟΞ΅ ΞΌΞ�Ξ½ΟΞΌΞ± ΞΌΞ΅ΟΞ¬ ΟΞ·Ξ½ Ξ΅Ξ½ΟΞΏΞ»Ξ�.")

@bot.message_handler(commands=['alert'])
def alert_command(message):
    if rate_limited(message.chat.id): return
    text = message.text.replace("/alert", "").strip()
    if text:
        bot.reply_to(message, "β οΈ Ξ£Ξ·ΞΌΞ±Ξ½ΟΞΉΞΊΞ� Ξ΅ΞΉΞ΄ΞΏΟΞΏΞ―Ξ·ΟΞ· ΞΊΞ±ΟΞ±Ξ³ΟΞ¬ΟΞ·ΞΊΞ΅!")
    else:
        bot.reply_to(message, "β Ξ Ξ±ΟΞ±ΞΊΞ±Ξ»Ο Ξ³ΟΞ¬ΟΞ΅ ΞΌΞ�Ξ½ΟΞΌΞ± ΞΌΞ΅ΟΞ¬ ΟΞ·Ξ½ Ξ΅Ξ½ΟΞΏΞ»Ξ�.")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if rate_limited(message.chat.id): return
    text = message.text.replace("/broadcast", "").strip()
    if text:
        bot.reply_to(message, "π£ ΞΞ½Ξ±ΞΊΞΏΞ―Ξ½ΟΟΞ· ΟΟΞ¬Ξ»ΞΈΞ·ΞΊΞ΅!")
    else:
        bot.reply_to(message, "β Ξ Ξ±ΟΞ±ΞΊΞ±Ξ»Ο Ξ³ΟΞ¬ΟΞ΅ ΞΌΞ�Ξ½ΟΞΌΞ± ΞΌΞ΅ΟΞ¬ ΟΞ·Ξ½ Ξ΅Ξ½ΟΞΏΞ»Ξ�.")

@bot.message_handler(commands=['log'])
def log_command(message):
    if rate_limited(message.chat.id): return
    try:
        with open("bot.log", "r") as log_file:
            lines = log_file.readlines()[-10:]
            response = "".join(lines) if lines else "ΞΞ΅Ξ½ ΟΟΞ¬ΟΟΞΏΟΞ½ ΞΊΞ±ΟΞ±Ξ³Ξ΅Ξ³ΟΞ±ΞΌΞΌΞ­Ξ½Ξ± logs."
            bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, "β Ξ£ΟΞ¬Ξ»ΞΌΞ± ΞΊΞ±ΟΞ¬ ΟΞ·Ξ½ Ξ±Ξ½Ξ¬Ξ³Ξ½ΟΟΞ· ΟΞΏΟ Ξ±ΟΟΞ΅Ξ―ΞΏΟ log.")

# ===== Flask route =====
@app.route('/')
def index():
    return "Bot is running!"

# ===== Webhook removal =====
def remove_webhook():
    url = f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook"
    try:
        requests.get(url, timeout=10)
        print("β Webhook Ξ΄ΞΉΞ±Ξ³ΟΞ¬ΟΞ·ΞΊΞ΅ Ξ΅ΟΞΉΟΟΟΟΟ.")
    except Exception as e:
        print("β οΈ Ξ£ΟΞ¬Ξ»ΞΌΞ± Ξ΄ΞΉΞ±Ξ³ΟΞ±ΟΞ�Ο webhook:", e)

# ===== Start Bot =====
if __name__ == "__main__":
    time.sleep(2)  # Delay Ξ³ΞΉΞ± Ξ½Ξ± ΟΞΉΞ³ΞΏΟΟΞ΅ΟΟΞΏΟΞΌΞ΅ ΟΟΞΉ ΟΞ»Ξ± Ξ­ΟΞΏΟΞ½ ΟΞΏΟΟΟΞΈΞ΅Ξ―
    remove_webhook()
    bot.polling(none_stop=True)