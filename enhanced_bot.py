import telebot
import logging
from flask import Flask, request
from datetime import datetime
import threading
import schedule
import time
import os

# Logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
)
logger = logging.getLogger()

# Token από environment variable
BOT_TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')

# Flask app
app = Flask(__name__)

# Δεδομένα χρήστη και έργων
user_data = {}

projects = {
    "bidprice": {
        "name": "BidPrice",
        "status": "Active",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Η πλατφόρμα BidPrice είναι σε λειτουργία και δέχεται προσφορές. Αναμένεται βελτιστοποίηση.",
        "logs": [
            "Η πλατφόρμα ενεργοποιήθηκε με επιτυχία.",
            "Ολοκληρώθηκε η αρχική δοκιμή MVP επιτυχώς."
        ],
        "metrics": {
            "active_listings": 24,
            "new_bids": 12,
            "progress": 75
        }
    },
    "amesis": {
        "name": "Amesis",
        "status": "In Development",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Η εφαρμογή Amesis είναι εργαλείο για επείγοντα pop-up μηνύματα.",
        "logs": [
            "Ξεκίνησε η δημιουργία διεπαφής.",
            "Ενσωματώθηκε αποστολή API μηνυμάτων."
        ],
        "metrics": {
            "messages_sent": 156,
            "recipients": 42,
            "progress": 60
        }
    },
    "6225": {
        "name": "Project6225",
        "status": "Planning",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Το project 6225 αφορά arbitrage & print-on-demand.",
        "logs": [
            "Έγινε καταγραφή στρατηγικής.",
            "Σχεδιάστηκε η δομή Shopify+Printify."
        ],
        "metrics": {
            "products": 11,
            "sales": 3,
            "progress": 35
        }
    }
}
# Εντολή /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message,
                 "Καλωσόρισες στο NOVAXA Bot!\n"
                 "Χρησιμοποίησε /help για διαθέσιμες εντολές.")

# Εντολή /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message,
                 "*Διαθέσιμες εντολές:*\n"
                 "/start - Εκκίνηση bot\n"
                 "/help - Βοήθεια\n"
                 "/status - Κατάσταση έργων\n"
                 "/log - Δες τα logs\n"
                 "/getid - Λήψη ID χρήστη\n"
                 "/broadcast <μήνυμα> - Μαζικό μήνυμα\n"
                 "/notify <κείμενο> - Υπενθύμιση")

# Εντολή /getid
@bot.message_handler(commands=['getid'])
def getid_command(message):
    bot.reply_to(message, f"Το Telegram ID σου είναι: `{message.from_user.id}`")

# Εντολή /status
@bot.message_handler(commands=['status'])
def status_command(message):
    text = "*Κατάσταση Έργων:*"
    for pid, data in projects.items():
        emoji = "🟢" if data['status'] == "Active" else "🔵"
        text += f"\n\n{emoji} *{data['name']}*\n"
        text += f"Κατάσταση: {data['status']}\n"
        text += f"Περιγραφή: {data['description']}\n"
        text += f"Τελευταία ενημέρωση: {data['last_update']}\n"
        text += f"Πρόοδος: {data['metrics'].get('progress', 0)}%\n"
    bot.reply_to(message, text)
# Εντολή /log για εμφάνιση logs (αν υπάρχει αρχείο)
@bot.message_handler(commands=['log'])
def log_command(message):
    try:
        if os.path.exists("log.txt"):
            with open("log.txt", "r", encoding="utf-8") as f:
                log_lines = f.readlines()[-20:]  # τελευταία 20 γραμμές
                response = "*Τελευταία Logs:*\n" + "".join(log_lines)
        else:
            response = "Δεν υπάρχουν καταγεγραμμένα logs."
        bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Σφάλμα κατά την ανάγνωση logs: {e}")

# Εντολή /broadcast για αποστολή σε όλους (μόνο admin)
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = message.from_user.id
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, "Παρακαλώ δώσε το μήνυμα που θέλεις να στείλεις.\nΠαράδειγμα:\n/broadcast Νέα ενημέρωση!")
        return
    text = " ".join(args)
    for uid in user_data:
        try:
            bot.send_message(uid, f"*Broadcast μήνυμα:*\n{text}", parse_mode='Markdown')
        except Exception as e:
            print(f"Αποτυχία αποστολής σε {uid}: {e}")
    bot.reply_to(message, "Το μήνυμα εστάλη σε όλους.")

# Εντολή /notify για μελλοντική υπενθύμιση
@bot.message_handler(commands=['notify'])
def notify_command(message):
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, "Παρακαλώ δώσε κείμενο υπενθύμισης.\nΠαράδειγμα:\n/notify Υπενθύμιση για ραντεβού")
        return
    notification_text = " ".join(args)
    uid = message.from_user.id
    # Προσθήκη στο user_data για παράδειγμα
    user_data[uid] = user_data.get(uid, {})
    user_data[uid]["reminder"] = notification_text
    bot.reply_to(message, f"Η υπενθύμιση καταγράφηκε:\n*{notification_text}*", parse_mode='Markdown')
# Inline κουμπιά για επιστροφή σε μενού projects
@bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_projects"))
def back_to_projects_callback(call):
    message_text = "📋 *Κατάσταση Projects* 📋\n\n"
    for project_id, project_data in projects.items():
        emoji = "🟢" if project_data["status"] == "Active" else \
                "🟡" if project_data["status"] == "In Development" else "🔵"
        message_text += f"{emoji} *{project_data['name']}*\n"
        message_text += f"Κατάσταση: {project_data['status']}\n"
        message_text += f"Περιγραφή: {project_data['description']}\n"
        message_text += f"Πρόοδος: {project_data['metrics']['progress']}%\n\n"
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("BidPrice", callback_data="project_bidprice"),
        types.InlineKeyboardButton("Amesis", callback_data="project_amesis"),
        types.InlineKeyboardButton("Project6225", callback_data="project_6225")
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=message_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

# Flask route για webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        return 'forbidden', 403

# Flask route για health check
@app.route('/')
def index():
    return "NOVAXA bot is running!", 200
# -------- SCHEDULER ΚΑΙ REPORTING -------- #

def get_uptime():
    try:
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))
        return uptime_str
    except Exception:
        return "Άγνωστο"

def send_daily_report():
    report_text = "📊 *Καθημερινή Αναφορά* 📊\n\n"
    for project_id, project in projects.items():
        emoji = "🟢" if project["status"] == "Active" else \
                "🟡" if project["status"] == "In Development" else "🔵"
        report_text += f"{emoji} *{project['name']}*\n"
        report_text += f"Κατάσταση: {project['status']}\n"
        report_text += f"Περιγραφή: {project['description']}\n"
        report_text += f"Πρόοδος: {project['metrics']['progress']}%\n\n"
    for user_id, user in user_data.items():
        try:
            bot.send_message(user["chat_id"], report_text, parse_mode='Markdown')
        except Exception as e:
            logger.warning(f"Αποτυχία αποστολής report σε χρήστη {user_id}: {e}")

def check_stock_alerts():
    alerts = stock_monitor.check_alerts()
    for alert in alerts:
        for user_id, user in user_data.items():
            try:
                bot.send_message(user["chat_id"], alert, parse_mode='Markdown')
            except Exception as e:
                logger.warning(f"Σφάλμα αποστολής alert σε χρήστη {user_id}: {e}")

def start_scheduler():
    schedule.every(30).minutes.do(check_stock_alerts)
    schedule.every().day.at("10:00").do(send_daily_report)
    while True:
        schedule.run_pending()
        time.sleep(1)
# -------- FLASK ROUTES + MAIN -------- #

@app.route('/', methods=['GET'])
def root():
    return 'NOVAXA Bot is running!', 200

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    try:
        webhook_url = f"{os.environ.get('WEBHOOK_URL')}/webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
        return f"Webhook set to {webhook_url}", 200
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return f"Error setting webhook: {e}", 500

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid content type', 403

def main():
    bot.remove_webhook()
    logger.info("Ξεκινάει polling...")
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    bot.polling(none_stop=True)

if __name__ == '__main__':
    if os.environ.get('WEBHOOK') == 'True':
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Ξεκινάει Flask app στο port {port}")
        app.run(host="0.0.0.0", port=port)
    else:
        main()

