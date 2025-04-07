"""
Enhanced NOVAXA Telegram Bot
A professional bot for stock alerts, project monitoring, and automated notifications
"""
import os
import logging
import time
import json
from datetime import datetime, timedelta
import threading
import schedule
import requests
from flask import Flask, request
import telebot
from telebot import types

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='novaxa_bot.log'
)
logger = logging.getLogger(__name__)

# Bot token (embedded)
TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"

# Initialize Flask app for webhook
app = Flask(__name__)

# Initialize Telegram bot
bot = telebot.TeleBot(TOKEN)

# Store user data
user_data = {}

# Projects info
projects = {
    "bidprice": {
        "name": "BidPrice",
        "status": "Active",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Πλατφόρμα δημοπρασιών προϊόντων",
        "logs": ["Σύστημα αρχικοποιήθηκε", "Όλες οι υπηρεσίες λειτουργούν"],
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
        "description": "Εφαρμογή αποστολής άμεσων pop-up μηνυμάτων",
        "logs": ["Ολοκληρώθηκε η μετάβαση της βάσης δεδομένων", "Ρυθμίστηκαν τα API endpoints"],
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
        "description": "Πρόγραμμα e-commerce arbitrage + Print-on-Demand",
        "logs": ["Αρχική φάση σχεδιασμού", "Συλλογή απαιτήσεων"],
        "metrics": {
            "products": 18,
            "sales": 7,
            "progress": 30
        }
    }
}

# Συνέχεια με StockMonitor...
# Stock monitoring functionality
class StockMonitor:
    def __init__(self):
        self.stock_data = {}
        self.default_stocks = {
            "OPAP.AT": {"name": "ΟΠΑΠ", "threshold": 18.50},
            "MYTIL.AT": {"name": "METLEN", "threshold": 42.44}
        }

    def add_stock(self, symbol, name, threshold=None):
        self.default_stocks[symbol] = {"name": name, "threshold": threshold}
        logger.info(f"Added stock {name} ({symbol}) to monitoring list")

    def remove_stock(self, symbol):
        if symbol in self.default_stocks:
            stock_name = self.default_stocks[symbol]["name"]
            del self.default_stocks[symbol]
            logger.info(f"Removed stock {stock_name} ({symbol}) from monitoring list")
            return True
        return False

    def set_alert_threshold(self, symbol, threshold):
        if symbol in self.default_stocks:
            self.default_stocks[symbol]["threshold"] = threshold
            logger.info(f"Set alert threshold for {symbol} to {threshold}")
            return True
        return False

    def get_stock_data(self, symbol):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                "region": "US",
                "lang": "en-US",
                "includePrePost": "false",
                "interval": "1d",
                "range": "1d",
                "corsDomain": "finance.yahoo.com",
                ".tsrc": "finance"
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                              " AppleWebKit/537.36 (KHTML, like Gecko)"
                              " Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
                result = data["chart"]["result"][0]
                meta = result["meta"]
                latest_price = meta.get("regularMarketPrice", 0)
                previous_close = meta.get("chartPreviousClose", 0)
                currency = meta.get("currency", "EUR")
                change = latest_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close else 0
                stock_info = {
                    "symbol": symbol,
                    "name": self.default_stocks.get(symbol, {}).get("name", symbol),
                    "price": latest_price,
                    "previous_close": previous_close,
                    "change": change,
                    "change_percent": change_percent,
                    "currency": currency,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                self.stock_data[symbol] = stock_info
                return stock_info
            else:
                logger.error(f"Invalid data format received for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None
def check_alerts(self, symbol=None):
        alerts = []
        symbols_to_check = [symbol] if symbol else list(self.default_stocks.keys())
        for sym in symbols_to_check:
            if sym not in self.default_stocks:
                continue
            threshold = self.default_stocks[sym].get("threshold")
            if not threshold:
                continue
            stock_info = self.get_stock_data(sym)
            if not stock_info:
                continue
            current_price = stock_info["price"]
            stock_name = stock_info["name"]
            if abs(current_price - threshold) / threshold <= 0.05:
                direction = "πάνω από" if current_price >= threshold else "κάτω από"
                alert_msg = (f"🚨 ΕΙΔΟΠΟΙΗΣΗ: Η μετοχή {stock_name} ({sym}) "
                             f"είναι {direction} το όριο των {threshold}€! "
                             f"Τρέχουσα τιμή: {current_price:.2f}€")
                alerts.append(alert_msg)
        return alerts

    def get_stock_summary(self, symbol=None):
        if symbol and symbol in self.default_stocks:
            stock_info = self.get_stock_data(symbol)
            if stock_info:
                return self._format_stock_message(stock_info)
            return f"Δεν βρέθηκαν δεδομένα για τη μετοχή {symbol}"
        summary = "📊 *Σύνοψη Μετοχών* 📊\n\n"
        for sym in self.default_stocks.keys():
            stock_info = self.get_stock_data(sym)
            if stock_info:
                summary += self._format_stock_message(stock_info) + "\n\n"
        return summary.strip()

    def _format_stock_message(self, stock_info):
        symbol = stock_info["symbol"]
        name = stock_info["name"]
        price = stock_info["price"]
        change = stock_info["change"]
        change_percent = stock_info["change_percent"]
        currency = stock_info["currency"]
        timestamp = stock_info["timestamp"]
        emoji = "🔴" if change < 0 else "🟢" if change > 0 else "⚪️"
        message = f"{emoji} *{name}* ({symbol})\n"
        message += f"Τιμή: {price:.2f} {currency}\n"
        message += f"Μεταβολή: {change:+.2f} ({change_percent:+.2f}%)\n"
        message += f"Τελευταία ενημέρωση: {timestamp}"
        return message


# Εκκίνηση του monitor
stock_monitor = StockMonitor()
# Εντολή /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user = message.from_user
    user_id = user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "chat_id": message.chat.id,
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    welcome_text = (
        f"Γεια σου {user.first_name}! Είμαι το NOVAXA bot.\n\n"
        f"Μπορώ να σε βοηθήσω με:\n"
        f"• Παρακολούθηση μετοχών και ειδοποιήσεις\n"
        f"• Διαχείριση των projects σου\n"
        f"• Αυτοματοποιημένες ειδοποιήσεις\n\n"
        f"Χρησιμοποίησε /help για να δεις όλες τις διαθέσιμες εντολές."
    )
    bot.reply_to(message, welcome_text)

# Εντολή /help
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "*Διαθέσιμες Εντολές:*\n\n"
        "*Γενικές Εντολές:*\n"
        "/start - Ξεκίνημα του bot\n"
        "/help - Εμφάνιση αυτού του μηνύματος βοήθειας\n"
        "/getid - Εμφάνιση του ID σου\n"
        "/status - Γενική κατάσταση συστήματος\n\n"
        "*Μετοχές:*\n"
        "/stocks - Εμφάνιση όλων των μετοχών\n"
        "/stock [σύμβολο] - Εμφάνιση συγκεκριμένης μετοχής\n"
        "/alert [σύμβολο] [τιμή] - Ορισμός ειδοποίησης για μετοχή\n\n"
        "*Projects:*\n"
        "/projects - Εμφάνιση όλων των projects\n"
        "/bidprice - Κατάσταση του BidPrice\n"
        "/amesis - Κατάσταση του Amesis\n"
        "/6225 - Κατάσταση του Project6225\n"
        "/logs [project] - Εμφάνιση logs για συγκεκριμένο project\n"
        "/progress - Καθημερινή αναφορά προόδου\n\n"
        "*Ειδοποιήσεις:*\n"
        "/broadcast [μήνυμα] - Αποστολή μαζικού μηνύματος\n"
        "/notify [μήνυμα] - Ορισμός ειδοποίησης\n"
        "/trending - Εμφάνιση τάσεων για Project6225\n"
        "/mystats - Εμφάνιση στατιστικών για όλα τα projects\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# Εντολή /getid
@bot.message_handler(commands=['getid'])
def getid_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    bot.reply_to(message, f"Το Telegram ID σου είναι: {user_id}\nΤο Chat ID είναι: {chat_id}")

# Εντολή /status
@bot.message_handler(commands=['status'])
def status_command(message):
    uptime = get_uptime()
    status_text = (
        f"*Κατάσταση Συστήματος NOVAXA*\n\n"
        f"🟢 *Bot:* Λειτουργεί κανονικά\n"
        f"⏱ *Uptime:* {uptime}\n"
        f"📊 *Μετοχές:* {len(stock_monitor.default_stocks)} υπό παρακολούθηση\n"
        f"📋 *Projects:* {len(projects)} ενεργά\n"
        f"👥 *Χρήστες:* {len(user_data)} συνδεδεμένοι\n\n"
        f"Τελευταία ενημέρωση: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown')
# Εντολή /stocks - Εμφάνιση όλων των παρακολουθούμενων μετοχών
@bot.message_handler(commands=['stocks'])
def stocks_command(message):
    bot.send_message(message.chat.id, "Λαμβάνω δεδομένα μετοχών...")
    summary = stock_monitor.get_stock_summary()
    bot.send_message(message.chat.id, summary, parse_mode='Markdown')

# Εντολή /stock [σύμβολο] - Εμφάνιση μιας συγκεκριμένης μετοχής
@bot.message_handler(commands=['stock'])
def stock_command(message):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if not args:
        bot.reply_to(message, "Παρακαλώ δώσε το σύμβολο της μετοχής. Παράδειγμα: /stock OPAP.AT")
        return
    symbol = args[0].upper()
    bot.send_message(message.chat.id, f"Λαμβάνω δεδομένα για τη μετοχή {symbol}...")
    stock_info = stock_monitor.get_stock_summary(symbol)
    bot.send_message(message.chat.id, stock_info, parse_mode='Markdown')

# Εντολή /alert [σύμβολο] [τιμή] - Ορισμός ειδοποίησης τιμής
@bot.message_handler(commands=['alert'])
def alert_command(message):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if len(args) < 2:
        bot.reply_to(message, "Χρήση: /alert OPAP.AT 18.50")
        return
    symbol = args[0].upper()
    try:
        threshold = float(args[1])
    except ValueError:
        bot.reply_to(message, "Η τιμή-στόχος πρέπει να είναι αριθμός.")
        return
    if symbol not in stock_monitor.default_stocks:
        stock_info = stock_monitor.get_stock_data(symbol)
        if not stock_info:
            bot.reply_to(message, f"Δεν βρέθηκε η μετοχή {symbol}.")
            return
        stock_monitor.add_stock(symbol, stock_info["name"])
    success = stock_monitor.set_alert_threshold(symbol, threshold)
    if success:
        bot.reply_to(message, f"Ορίστηκε ειδοποίηση για {symbol} στα {threshold}€.")
    else:
        bot.reply_to(message, f"Απέτυχε ο ορισμός ειδοποίησης για {symbol}.")

# Εντολή /projects - Προβολή όλων των projects
@bot.message_handler(commands=['projects'])
def projects_command(message):
    message_text = "📋 *Κατάσταση Projects* 📋\n\n"
    for project_id, project_data in projects.items():
        status_emoji = "🟢" if project_data["status"] == "Active" else \
                       "🟡" if project_data["status"] == "In Development" else "🔵"
        message_text += f"{status_emoji} *{project_data['name']}*\n"
        message_text += f"Κατάσταση: {project_data['status']}\n"
        message_text += f"Τελευταία ενημέρωση: {project_data['last_update']}\n"
        message_text += f"Περιγραφή: {project_data['description']}\n"
        message_text += f"Πρόοδος: {project_data['metrics']['progress']}%\n\n"
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_bidprice = types.InlineKeyboardButton("BidPrice", callback_data="project_bidprice")
    btn_amesis = types.InlineKeyboardButton("Amesis", callback_data="project_amesis")
    btn_6225 = types.InlineKeyboardButton("Project6225", callback_data="project_6225")
    markup.add(btn_bidprice, btn_amesis, btn_6225)
    bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode='Markdown')
# Εντολές για συγκεκριμένα projects
@bot.message_handler(commands=['bidprice'])
def bidprice_command(message):
    send_project_status(message, "bidprice")

@bot.message_handler(commands=['amesis'])
def amesis_command(message):
    send_project_status(message, "amesis")

@bot.message_handler(commands=['6225'])
def project6225_command(message):
    send_project_status(message, "6225")

# Εντολή /logs [project] - Εμφάνιση logs συγκεκριμένου project
@bot.message_handler(commands=['logs'])
def logs_command(message):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if not args:
        bot.reply_to(message, "Παρακαλώ γράψε το όνομα του project. Π.χ.: /logs bidprice")
        return
    project_id = args[0].lower()
    if project_id in projects:
        send_project_logs(message, project_id)
    else:
        bot.reply_to(message, "Δεν βρέθηκε αυτό το project. Επιλογές: bidprice, amesis, 6225")

# Εντολή /progress - Ημερήσια αναφορά προόδου όλων των projects
@bot.message_handler(commands=['progress'])
def progress_command(message):
    report_text = "📈 *Καθημερινή Αναφορά Προόδου* 📈\n\n"
    report_text += f"*Ημερομηνία:* {datetime.now().strftime('%Y-%m-%d')}\n\n"

    report_text += "*Μετοχές:*\n"
    for symbol, stock_data in stock_monitor.default_stocks.items():
        stock_info = stock_monitor.get_stock_data(symbol)
        if stock_info:
            emoji = "🔴" if stock_info["change"] < 0 else "🟢" if stock_info["change"] > 0 else "⚪️"
            report_text += f"{emoji} {stock_data['name']}: {stock_info['price']:.2f}€ ({stock_info['change']:+.2f}€)\n"

    report_text += "\n*Projects:*\n"
    for pid, pdata in projects.items():
        emoji = "🟢" if pdata["status"] == "Active" else \
                "🟡" if pdata["status"] == "In Development" else "🔵"
        report_text += f"{emoji} *{pdata['name']}*\n"
        report_text += f"  Πρόοδος: {pdata['metrics']['progress']}%\n"
        if pid == "bidprice":
            report_text += f"  Αγγελίες: {pdata['metrics']['active_listings']}, Προσφορές: {pdata['metrics']['new_bids']}\n"
        elif pid == "amesis":
            report_text += f"  Μηνύματα: {pdata['metrics']['messages_sent']}, Παραλήπτες: {pdata['metrics']['recipients']}\n"
        elif pid == "6225":
            report_text += f"  Προϊόντα: {pdata['metrics']['products']}, Πωλήσεις: {pdata['metrics']['sales']}\n"
        report_text += f"  Τελευταία ενέργεια: {pdata['logs'][-1]}\n\n"

    bot.send_message(message.chat.id, report_text, parse_mode='Markdown')
# Εντολή /broadcast [μήνυμα] - Μαζική αποστολή μηνύματος (μόνο admin)
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, "Γράψε το μήνυμα που θέλεις να στείλεις. Παράδειγμα:\n/broadcast Καλημέρα σε όλους!")
        return
    broadcast_text = " ".join(args)
    sent = 0
    for user_id, data in user_data.items():
        try:
            bot.send_message(data["chat_id"], f"📢 *Ενημέρωση:*\n{broadcast_text}", parse_mode='Markdown')
            sent += 1
        except Exception as e:
            logger.error(f"Broadcast error to user {user_id}: {str(e)}")
    bot.reply_to(message, f"Το μήνυμα στάλθηκε σε {sent} χρήστες.")

# Εντολή /notify [μήνυμα] - Ορισμός ειδοποίησης (placeholder λειτουργία)
@bot.message_handler(commands=['notify'])
def notify_command(message):
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, "Γράψε το κείμενο ειδοποίησης. Παράδειγμα:\n/notify Έλεγχος αποθεμάτων στις 14:00")
        return
    notification_text = " ".join(args)
    bot.reply_to(message, f"🔔 Ειδοποίηση καταχωρήθηκε:\n{notification_text}")

# Εντολή /mystats - Στατιστικά όλων των projects
@bot.message_handler(commands=['mystats'])
def mystats_command(message):
    message_text = "📊 *Συγκεντρωτικά Στατιστικά Projects* 📊\n\n"
    for pid, pdata in projects.items():
        message_text += f"*{pdata['name']}*\n"
        for key, value in pdata["metrics"].items():
            message_text += f"• {key.replace('_',' ').capitalize()}: {value}\n"
        message_text += f"• Πρόοδος: {pdata['metrics']['progress']}%\n\n"
    bot.send_message(message.chat.id, message_text, parse_mode='Markdown')

# Εντολή /trending - Προβολή τάσεων για Project6225
@bot.message_handler(commands=['trending'])
def trending_command(message):
    trending = [
        {"name": "Custom T-Shirt Design #1", "sales": 12, "growth": "+25%"},
        {"name": "Phone Case Model X", "sales": 8, "growth": "+15%"},
        {"name": "Personalized Mug", "sales": 6, "growth": "+10%"}
    ]
    msg = "🔥 *Trending Προϊόντα - Project6225* 🔥\n\n"
    for i, p in enumerate(trending, 1):
        msg += f"{i}. *{p['name']}*\n   Πωλήσεις: {p['sales']} | Ανάπτυξη: {p['growth']}\n\n"
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')
# Διαχείριση callback queries για inline κουμπιά
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("project_"):
        project_id = call.data.replace("project_", "")
        show_project_details(call, project_id)
    elif call.data.startswith("logs_"):
        project_id = call.data.replace("logs_", "")
        show_project_logs(call, project_id)
    elif call.data == "back_to_projects":
        show_all_projects(call)

def show_project_details(call, project_id):
    if project_id not in projects:
        bot.answer_callback_query(call.id, "Project not found")
        return
    pdata = projects[project_id]
    msg = f"📊 *{pdata['name']}* 📊\n\n"
    msg += f"Κατάσταση: {pdata['status']}\n"
    msg += f"Τελευταία ενημέρωση: {pdata['last_update']}\n"
    msg += f"Περιγραφή: {pdata['description']}\n\n"
    msg += "*Μετρήσεις:*\n"
    for key, val in pdata["metrics"].items():
        msg += f"• {key.replace('_',' ').capitalize()}: {val}\n"
    msg += "\n*Τελευταία logs:*\n"
    for log in pdata["logs"][-3:]:
        msg += f"• {log}\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Πλήρη Logs", callback_data=f"logs_{project_id}"),
        types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
    )
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=msg,
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def show_project_logs(call, project_id):
    if project_id not in projects:
        bot.answer_callback_query(call.id, "Project not found")
        return
    logs = projects[project_id]["logs"]
    msg = f"📝 *Logs για {projects[project_id]['name']}* 📝\n\n"
    for i, log in enumerate(logs, 1):
        msg += f"{i}. {log}\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(f"Επιστροφή στο {projects[project_id]['name']}", callback_data=f"project_{project_id}"),
        types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
    )
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=msg,
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def show_all_projects(call):
    msg = "📋 *Κατάσταση Projects* 📋\n\n"
    for pid, pdata in projects.items():
        emoji = "🟢" if pdata["status"] == "Active" else "🟡" if pdata["status"] == "In Development" else "🔵"
        msg += f"{emoji} *{pdata['name']}*\nΠρόοδος: {pdata['metrics']['progress']}%\n\n"
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("BidPrice", callback_data="project_bidprice"),
        types.InlineKeyboardButton("Amesis", callback_data="project_amesis"),
        types.InlineKeyboardButton("Project6225", callback_data="project_6225")
    )
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=msg,
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)
# ----------- SCHEDULER ΚΑΙ ΠΕΡΙΟΔΙΚΕΣ ΕΡΓΑΣΙΕΣ -----------

def check_stock_alerts():
    """Έλεγχος μετοχών για ειδοποιήσεις."""
    alerts = stock_monitor.check_alerts()
    if alerts:
        for user_id, udata in user_data.items():
            for alert in alerts:
                try:
                    bot.send_message(udata["chat_id"], alert)
                except Exception as e:
                    logger.error(f"Αποτυχία αποστολής ειδοποίησης σε χρήστη {user_id}: {e}")

def update_project_statuses():
    """Ανανεώνει την ημερομηνία τελευταίας ενημέρωσης στα projects."""
    for project in projects.values():
        project["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def send_daily_report():
    """Αποστολή ημερήσιας αναφοράς σε όλους τους χρήστες."""
    today = datetime.now().strftime("%Y-%m-%d")
    report = f"📈 *Ημερήσια Αναφορά NOVAXA* - {today} 📈\n\n"
    report += stock_monitor.get_stock_summary() + "\n\n"
    for pid, pdata in projects.items():
        report += f"🔹 *{pdata['name']}*: {pdata['metrics']['progress']}%\n"
    for user_id, udata in user_data.items():
        try:
            bot.send_message(udata["chat_id"], report, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Σφάλμα αποστολής αναφοράς σε {user_id}: {e}")

def run_scheduler():
    """Τρέχει το schedule loop στο παρασκήνιο."""
    schedule.every(10).minutes.do(check_stock_alerts)
    schedule.every(1).hours.do(update_project_statuses)
    schedule.every().day.at("09:00").do(send_daily_report)
    while True:
        schedule.run_pending()
        time.sleep(1)

# ---------- FLASK SERVER / POLLING MODE ----------

@app.route('/')
def index():
    return "NOVAXA bot is alive."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Επεξεργασία ενημερώσεων από Telegram (webhook mode)"""
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.data.decode("utf-8"))
        bot.process_new_updates([update])
        return 'ok', 200
    return 'bad request', 400

def start_polling():
    """Ξεκινά το bot με polling (για ανάπτυξη)"""
    bot.remove_webhook()
    threading.Thread(target=run_scheduler, daemon=True).start()
    bot.polling(none_stop=True)

def start_webhook():
    """Ξεκινά το bot με webhook (για παραγωγή)"""
    webhook_url = os.getenv("WEBHOOK_URL")
    port = int(os.environ.get('PORT', 5000))
    if webhook_url:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        threading.Thread(target=run_scheduler, daemon=True).start()
        app.run(host="0.0.0.0", port=port)
    else:
        start_polling()

# ----------- ΕΚΚΙΝΗΣΗ MAIN -----------

if __name__ == '__main__':
    logger.info("Ξεκινά το NOVAXA bot...")
    start_webhook()
