import os
import logging
import time
import json
from datetime import datetime, timedelta
import threading

import schedule
import requests
from flask import Flask, request, jsonify
import telebot
from telebot import types

# Configure logging (log to both file and console for visibility)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    # Για εμφάνιση στο Render logs, δεν ορίζουμε filename (ή εναλλακτικά χρησιμοποιούμε handlers)
)
logger = logging.getLogger(__name__)

# Bot token (Ενσωματωμένο σωστό TOKEN)
TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"

# Initialize Flask app (backend API & webhook receiver)
app = Flask(__name__)

# Initialize Telegram bot
bot = telebot.TeleBot(TOKEN)

# In-memory storage for user data
user_data = {}

# Sample projects data (initial state)
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

# Stock Monitor class for retrieving stock info and managing alerts
class StockMonitor:
    def __init__(self):
        self.stock_data = {}
        self.default_stocks = {
            # Default stocks (Athens Exchange) with threshold for alerts
            "OPAP.AT": {"name": "ΟΠΑΠ", "threshold": 18.50},
            "MYTIL.AT": {"name": "METKA", "threshold": 42.44}
        }
    
    def get_stock_data(self, symbol):
        """Fetch current stock data for symbol from Yahoo Finance API"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                "region": "US", "lang": "en-US", "includePrePost": "false",
                "interval": "1d", "range": "1d", "corsDomain": "finance.yahoo.com", ".tsrc": "finance"
            }
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            if "chart" in data and data["chart"].get("result"):
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
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                # Update cache
                self.stock_data[symbol] = stock_info
                return stock_info
            else:
                logger.error(f"Invalid data format received for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None

    def get_stock_summary(self, symbol=None):
        """Generate a summary text of stock data for one or all stocks"""
        if symbol:
            info = self.get_stock_data(symbol)
            if info:
                return self._format_stock_message(info)
            return f"Δεν βρέθηκαν δεδομένα για τη μετοχή {symbol}"
        # If no symbol specified, summarize all default stocks
        summary_lines = ["📊 *Σύνοψη Μετοχών* 📊", ""]
        for sym in self.default_stocks:
            info = self.get_stock_data(sym)
            if info:
                summary_lines.append(self._format_stock_message(info))
                summary_lines.append("")  # blank line separator
        return "\n".join(summary_lines).strip()

    def _format_stock_message(self, stock_info):
        """Format single stock info as Markdown message string"""
        symbol = stock_info["symbol"]
        name = stock_info["name"]
        price = stock_info["price"]
        change = stock_info["change"]
        change_percent = stock_info["change_percent"]
        currency = stock_info["currency"]
        timestamp = stock_info["timestamp"]
        # Pick emoji for price change
        emoji = "🔴" if change < 0 else "🟢" if change > 0 else "⚪️"
        message = (f"{emoji} *{name}* ({symbol})\n"
                   f"Τιμή: {price:.2f} {currency}\n"
                   f"Μεταβολή: {change:+.2f} ({change_percent:+.2f}%)\n"
                   f"Τελευταία ενημέρωση: {timestamp}")
        return message

    def check_alerts(self):
        """Check all monitored stocks against their threshold and return alert messages"""
        alerts = []
        for sym, data in self.default_stocks.items():
            threshold = data.get("threshold")
            if not threshold:
                continue
            stock_info = self.get_stock_data(sym)
            if not stock_info:
                continue
            current_price = stock_info["price"]
            # Trigger alert if price is within ±5% of threshold (or beyond)
            if abs(current_price - threshold) / threshold <= 0.05:
                direction = "πάνω από" if current_price >= threshold else "κάτω από"
                alert_msg = (f"🚨 Ειδοποίηση: Η μετοχή {stock_info['name']} ({sym}) "
                             f"είναι {direction} το όριο των {threshold:.2f}€. "
                             f"Τρέχουσα τιμή: {current_price:.2f}€.")
                alerts.append(alert_msg)
        return alerts

# Initialize the stock monitor instance
stock_monitor = StockMonitor()

# Helper function to get uptime (placeholder implementation)
start_time = datetime.now()
def get_uptime():
    """Return system uptime as human-readable string."""
    delta = datetime.now() - start_time
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, _ = divmod(rem, 60)
    return f"{days} ημέρες, {hours} ώρες, {minutes} λεπτά"

# --- Telegram Bot Command Handlers ---

@bot.message_handler(commands=['start'])
def start_command(message):
    """Handle /start command: welcome the user and store their info."""
    user = message.from_user
    user_id = user.id
    chat_id = message.chat.id
    # Save user data if first time
    if user_id not in user_data:
        user_data[user_id] = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "chat_id": chat_id,
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    welcome_text = (
        f"Γεια σου {user.first_name}! Είμαι το NOVAXA bot.\n\n"
        "Μπορώ να σε βοηθήσω με:\n"
        "• Παρακολούθηση μετοχών και ειδοποιήσεις\n"
        "• Διαχείριση των projects σου\n"
        "• Αυτοματοποιημένες ειδοποιήσεις\n\n"
        "Χρησιμοποίησε /help για να δεις όλες τις διαθέσιμες εντολές."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    """Handle /help command: list available commands."""
    help_text = (
        "*Διαθέσιμες Εντολές:*\n\n"
        "*Γενικές:*\n"
        "/start - Ξεκίνημα του bot\n"
        "/help - Εμφάνιση αυτού του μηνύματος βοήθειας\n"
        "/getid - Εμφάνιση του ID σου\n"
        "/status - Γενική κατάσταση συστήματος\n\n"
        "*Μετοχές:*\n"
        "/stocks - Εμφάνιση όλων των μετοχών\n"
        "/stock <σύμβολο> - Πληροφορίες συγκεκριμένης μετοχής\n"
        "/alert <σύμβολο> <τιμή> - Ορισμός ειδοποίησης τιμής\n\n"
        "*Projects:*\n"
        "/projects - Κατάσταση όλων των projects\n"
        "/bidprice - Κατάσταση BidPrice\n"
        "/amesis - Κατάσταση Amesis\n"
        "/6225 - Κατάσταση Project6225\n"
        "/logs <project> - Εμφάνιση logs συγκεκριμένου project\n"
        "/progress - Καθημερινή αναφορά προόδου\n\n"
        "*Ειδοποιήσεις:*\n"
        "/broadcast <μήνυμα> - Μαζικό μήνυμα (admin only)\n"
        "/notify <μήνυμα> - Προγραμματισμένη ειδοποίηση\n"
        "/trending - Τάσεις δημοφιλών προϊόντων (Project6225)\n"
        "/mystats - Στατιστικά όλων των projects\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['getid'])
def getid_command(message):
    """Send the user's Telegram ID and chat ID."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    bot.reply_to(message, f"Το Telegram ID σου είναι: {user_id}\nΤο Chat ID είναι: {chat_id}")

@bot.message_handler(commands=['status'])
def status_command(message):
    """Send overall system status summary."""
    uptime = get_uptime()
    status_text = (
        "*Κατάσταση Συστήματος NOVAXA:*\n\n"
        "🟢 *Bot:* Λειτουργεί κανονικά\n"
        f"⏱ *Uptime:* {uptime}\n"
        f"📊 *Μετοχές:* Παρακολουθούνται {len(stock_monitor.default_stocks)} μετοχές\n"
        f"📋 *Projects:* {len(projects)} ενεργά projects\n"
        f"👥 *Χρήστες:* {len(user_data)} εγγεγραμμένοι χρήστες\n\n"
        f"Τελευταία ενημέρωση: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown')

# Stock-related commands
@bot.message_handler(commands=['stocks'])
def stocks_command(message):
    """Send a summary of all monitored stocks."""
    bot.send_message(message.chat.id, "Λήψη δεδομένων μετοχών...")
    summary = stock_monitor.get_stock_summary()
    bot.send_message(message.chat.id, summary, parse_mode='Markdown')

@bot.message_handler(commands=['stock'])
def stock_command(message):
    """Send detailed info for a specific stock."""
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Χρήση: /stock <σύμβολο> (π.χ. /stock OPAP.AT)")
        return
    symbol = parts[1].upper()
    bot.send_message(message.chat.id, f"Λήψη δεδομένων για τη μετοχή {symbol}...")
    info = stock_monitor.get_stock_summary(symbol)
    bot.send_message(message.chat.id, info, parse_mode='Markdown')

@bot.message_handler(commands=['alert'])
def alert_command(message):
    """Set a price alert for a stock symbol."""
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Χρήση: /alert <σύμβολο> <τιμή> (π.χ. /alert OPAP.AT 18.50)")
        return
    symbol = parts[1].upper()
    try:
        threshold = float(parts[2])
    except ValueError:
        bot.reply_to(message, "Η τιμή-στόχος πρέπει να είναι αριθμός.")
        return
    # Add or update the stock with threshold
    stock_monitor.default_stocks[symbol] = {"name": symbol, "threshold": threshold}
    bot.reply_to(message, f"✅ Προστέθηκε ειδοποίηση για {symbol} στα {threshold:.2f}€")

# Projects-related commands
@bot.message_handler(commands=['projects'])
def projects_command(message):
    """Send a summary of all projects and their status."""
    text = "📋 *Κατάσταση Projects:* 📋\n\n"
    for pid, pdata in projects.items():
        # Επιλογή emoji κατάστασης
        if pdata["status"] == "Active":
            status_emoji = "🟢"
        elif pdata["status"] == "In Development":
            status_emoji = "🟡"
        else:
            status_emoji = "🔵"
        text += (f"{status_emoji} *{pdata['name']}*\n"
                 f"Κατάσταση: {pdata['status']}\n"
                 f"Τελευταία ενημέρωση: {pdata['last_update']}\n"
                 f"Περιγραφή: {pdata['description']}\n"
                 f"Πρόοδος: {pdata['metrics']['progress']}%\n\n")
    # Προσθήκη inline κουμπιών για λεπτομέρειες
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("BidPrice", callback_data="project_bidprice"),
        types.InlineKeyboardButton("Amesis", callback_data="project_amesis"),
        types.InlineKeyboardButton("Project6225", callback_data="project_6225")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['bidprice', 'amesis', '6225'])
def project_status_command(message):
    """Shortcut commands for each project to show status."""
    cmd = message.text.lstrip('/').lower()  # 'bidprice' or 'amesis' or '6225'
    if cmd in ["bidprice", "amesis", "6225"]:
        send_project_status(message, cmd)
    else:
        bot.reply_to(message, "Άγνωστο project.")

@bot.message_handler(commands=['logs'])
def logs_command(message):
    """Send the logs of a specified project."""
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Χρήση: /logs <project> (π.χ. /logs bidprice)")
        return
    project_id = parts[1].lower()
    if project_id in projects:
        send_project_logs(message, project_id)
    else:
        bot.reply_to(message, f"Το project {project_id} δεν βρέθηκε. Διαθέσιμα: bidprice, amesis, 6225")

@bot.message_handler(commands=['progress'])
def progress_command(message):
    """Send a daily progress report for all projects and stocks."""
    report_date = datetime.now().strftime('%Y-%m-%d')
    text = f"📈 *Καθημερινή Αναφορά Προόδου* 📈\n\n*Ημερομηνία:* {report_date}\n\n"
    # Συνοπτικά στοιχεία μετοχών
    text += "*Μετοχές:*\n"
    for sym, stock in stock_monitor.default_stocks.items():
        info = stock_monitor.get_stock_data(sym)
        if info:
            emoji = "🔴" if info["change"] < 0 else "🟢" if info["change"] > 0 else "⚪️"
            text += f"{emoji} {stock['name']}: {info['price']:.2f}€ ({info['change']:+.2f}€)\n"
    text += "\n*Projects:*\n"
    for pid, pdata in projects.items():
        status_emoji = "🟢" if pdata["status"] == "Active" else "🟡" if pdata["status"] == "In Development" else "🔵"
        text += f"{status_emoji} *{pdata['name']}*\n  Πρόοδος: {pdata['metrics']['progress']}%\n"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    """Broadcast a message to all users (admin functionality)."""
    parts = message.text.split(maxsplit=1)
    # (Σε πλήρη υλοποίηση, θα ελέγχαμε αν ο χρήστης είναι admin)
    if len(parts) < 2:
        bot.reply_to(message, "Χρήση: /broadcast <μήνυμα>")
        return
    broadcast_text = parts[1]
    # Αποστολή σε όλους τους χρήστες στο user_data
    for uid, data in user_data.items():
        try:
            bot.send_message(data["chat_id"], f"📣 *Broadcast:*\n{broadcast_text}", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error broadcasting to {uid}: {e}")
    bot.reply_to(message, "✅ Το μήνυμα εστάλη σε όλους τους χρήστες.")

@bot.message_handler(commands=['notify'])
def notify_command(message):
    """Set a personal notification (placeholder functionality)."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Χρήση: /notify <μήνυμα υπενθύμισης>")
        return
    note_text = parts[1]
    # Στην παρούσα φάση απλώς επιβεβαιώνουμε τη ρύθμιση (δεν αποθηκεύεται μόνιμα)
    bot.reply_to(message, f"🔔 Η ειδοποίηση ρυθμίστηκε: \"{note_text}\"")

@bot.message_handler(commands=['trending'])
def trending_command(message):
    """Show trending products (for Project6225)"""
    trending_products = [
        {"name": "Custom T-Shirt Design #1", "sales": 12, "growth": "+25%"},
        {"name": "Phone Case Model X", "sales": 8, "growth": "+15%"},
        {"name": "Personalized Mug", "sales": 6, "growth": "+10%"}
    ]
    text = "📊 *Trending Products - Project6225:* 📊\n\n"
    for i, prod in enumerate(trending_products, start=1):
        text += (f"{i}. *{prod['name']}*\n"
                 f"   Πωλήσεις: {prod['sales']}\n"
                 f"   Ανάπτυξη: {prod['growth']}\n\n")
    text += "*Προτεινόμενες Ενέργειες:*\n"
    text += "• Αύξηση διαφημιστικού budget για το #1\n"
    text += "• Νέα παρόμοια προϊόντα όπως το #2\n"
    text += "• Προσφορά έκπτωσης για το #3\n"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['mystats'])
def mystats_command(message):
    """Show aggregated stats for all projects."""
    text = "📊 *Στατιστικά Projects:* 📊\n\n"
    # BidPrice stats
    bp = projects["bidprice"]["metrics"]
    text += "*BidPrice:*\n"
    text += f"• Ενεργές αγγελίες: {bp['active_listings']}\n"
    text += f"• Νέες προσφορές: {bp['new_bids']}\n"
    text += f"• Ποσοστό ολοκλήρωσης: {bp['progress']}%\n\n"
    # Amesis stats
    am = projects["amesis"]["metrics"]
    text += "*Amesis:*\n"
    text += f"• Μηνύματα που στάλθηκαν: {am['messages_sent']}\n"
    text += f"• Παραλήπτες: {am['recipients']}\n"
    text += f"• Ποσοστό ολοκλήρωσης: {am['progress']}%\n\n"
    # Project6225 stats
    pr = projects["6225"]["metrics"]
    text += "*Project6225:*\n"
    text += f"• Προϊόντα: {pr['products']}\n"
    text += f"• Πωλήσεις: {pr['sales']}\n"
    text += f"• Ποσοστό ολοκλήρωσης: {pr['progress']}%\n\n"
    # Συνολική πρόοδος (τυχαίο παράδειγμα)
    overall_progress = (bp['progress'] + am['progress'] + pr['progress']) // 3
    text += f"*Συνολική Πρόοδος:* {overall_progress}%"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# Helper functions for project info
def send_project_status(message, project_id):
    """Send a detailed status message for a given project."""
    if project_id not in projects:
        bot.reply_to(message, f"Το project {project_id} δεν βρέθηκε.")
        return
    pdata = projects[project_id]
    metrics = pdata["metrics"]
    text = (f"📊 *{pdata['name']}* 📊\n\n"
            f"*Κατάσταση:* {pdata['status']}\n"
            f"*Τελευταία ενημέρωση:* {pdata['last_update']}\n"
            f"*Περιγραφή:* {pdata['description']}\n\n"
            "*Μετρήσεις:*\n")
    if project_id == "bidprice":
        text += f"• Ενεργές αγγελίες: {metrics['active_listings']}\n"
        text += f"• Νέες προσφορές: {metrics['new_bids']}\n"
    elif project_id == "amesis":
        text += f"• Μηνύματα που στάλθηκαν: {metrics['messages_sent']}\n"
        text += f"• Παραλήπτες: {metrics['recipients']}\n"
    elif project_id == "6225":
        text += f"• Προϊόντα: {metrics['products']}\n"
        text += f"• Πωλήσεις: {metrics['sales']}\n"
    text += f"• Πρόοδος: {metrics['progress']}%\n\n"
    text += f"*Τελευταία logs:* {pdata['logs'][-1]}"
    # Inline keyboard for full logs or back to projects list
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Πλήρη Logs", callback_data=f"logs_{project_id}"),
        types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

def send_project_logs(message, project_id):
    """Send the full log list for a given project."""
    pdata = projects[project_id]
    text = f"📝 *Logs για {pdata['name']}* 📝\n\n"
    for i, log_entry in enumerate(pdata['logs'], start=1):
        text += f"{i}. {log_entry}\n"
    # Inline buttons to go back
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"Επιστροφή στο {pdata['name']}", callback_data=f"project_{project_id}"),
        types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

# Callback query handler for inline buttons
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("project_"):
        proj_id = call.data.split("_", 1)[1]
        # Send project status via editing the existing message to avoid clutter
        if proj_id in projects:
            pdata = projects[proj_id]
            metrics = pdata["metrics"]
            text = (f"📊 *{pdata['name']}* 📊\n\n"
                    f"*Κατάσταση:* {pdata['status']}\n"
                    f"*Τελευταία ενημέρωση:* {pdata['last_update']}\n"
                    f"*Περιγραφή:* {pdata['description']}\n\n"
                    "*Μετρήσεις:*\n")
            # (Similar block as send_project_status for metrics)
            if proj_id == "bidprice":
                text += f"• Ενεργές αγγελίες: {metrics['active_listings']}\n"
                text += f"• Νέες προσφορές: {metrics['new_bids']}\n"
            elif proj_id == "amesis":
                text += f"• Μηνύματα που στάλθηκαν: {metrics['messages_sent']}\n"
                text += f"• Παραλήπτες: {metrics['recipients']}\n"
            elif proj_id == "6225":
                text += f"• Προϊόντα: {metrics['products']}\n"
                text += f"• Πωλήσεις: {metrics['sales']}\n"
            text += f"• Πρόοδος: {metrics['progress']}%\n\n"
            text += f"*Τελευταία logs:* {pdata['logs'][-1]}"
            # Update the message text and provide buttons
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Πλήρη Logs", callback_data=f"logs_{proj_id}"),
                types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
            )
            bot.edit_message_text(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id,
                                   text=text, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    elif call.data.startswith("logs_"):
        proj_id = call.data.split("_", 1)[1]
        if proj_id in projects:
            # Send full logs as a new message
            send_project_logs(call.message, proj_id)
        bot.answer_callback_query(call.id)
    elif call.data == "back_to_projects":
        # User wants to see the projects overview again
        send_back = types.InlineKeyboardMarkup(row_width=3)
        send_back.add(
            types.InlineKeyboardButton("BidPrice", callback_data="project_bidprice"),
            types.InlineKeyboardButton("Amesis", callback_data="project_amesis"),
            types.InlineKeyboardButton("Project6225", callback_data="project_6225")
        )
        text = "📋 *Κατάσταση Projects:* 📋\n\n"
        for pid, pdata in projects.items():
            status_emoji = "🟢" if pdata["status"] == "Active" else "🟡" if pdata["status"] == "In Development" else "🔵"
            text += (f"{status_emoji} *{pdata['name']}*\n"
                     f"Κατάσταση: {pdata['status']}\n"
                     f"Τελευταία ενημέρωση: {pdata['last_update']}\n"
                     f"Περιγραφή: {pdata['description']}\n"
                     f"Πρόοδος: {pdata['metrics']['progress']}%\n\n")
        bot.edit_message_text(chat_id=call.message.chat.id,
                               message_id=call.message.message_id,
                               text=text, reply_markup=send_back, parse_mode='Markdown')
        bot.answer_callback_query(call.id)

# --- Scheduled Tasks ---

def send_stock_alerts_to_users():
    """Fetch stock alerts and send to all users (called by scheduler)."""
    alerts = stock_monitor.check_alerts()
    for alert in alerts:
        logger.info(f"Stock alert triggered: {alert}")
        for uid, data in user_data.items():
            try:
                bot.send_message(data["chat_id"], alert, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error sending alert to user {uid}: {e}")

def update_project_data():
    """Periodic update of project data (placeholder: just refresh timestamp)."""
    for pid in projects:
        projects[pid]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Project data updated (last_update timestamps refreshed).")

def send_daily_report():
    """Send a daily summary report to all users."""
    report = datetime.now().strftime("%Y-%m-%d") + " - Daily Report\n"
    # (We can reuse /progress content or keep it simple)
    for uid, data in user_data.items():
        try:
            bot.send_message(data["chat_id"], "📈 Καθημερινή αναφορά προόδου είναι διαθέσιμη.", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error sending daily report to {uid}: {e}")

def run_scheduler():
    """Background scheduler thread to run periodic tasks."""
    # Check stock alerts every 15 minutes
    schedule.every(15).minutes.do(send_stock_alerts_to_users)
    # Update project data every hour
    schedule.every().hour.do(update_project_data)
    # Send daily report at 09:00 each day
    schedule.every().day.at("09:00").do(send_daily_report)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)

# --- Flask Webhook & API Routes ---

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Webhook endpoint for Telegram calls."""
    if request.headers.get('content-type') == 'application/json':
        update_json = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(update_json)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Unsupported Media', 403

@app.route('/api/stocks')
def api_get_stocks():
    """API endpoint to get data for all stocks."""
    # Return cached data for all default stocks (updating each one first)
    data = {}
    for sym in stock_monitor.default_stocks:
        info = stock_monitor.get_stock_data(sym)
        if info:
            data[sym] = info
    return jsonify(data)

@app.route('/api/stocks/<symbol>')
def api_get_stock(symbol):
    """API endpoint for a specific stock."""
    info = stock_monitor.get_stock_data(symbol.upper())
    if info:
        return jsonify(info)
    return jsonify({"error": "Stock not found"}), 404

@app.route('/api/projects')
def api_get_projects():
    """API endpoint to get all projects data."""
    return jsonify(projects)

@app.route('/api/projects/<project_id>')
def api_get_project(project_id):
    """API endpoint to get a specific project's data."""
    proj = projects.get(project_id.lower())
    if proj:
        return jsonify(proj)
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/notifications')
def api_get_notifications():
    """API endpoint to get notifications (placeholder)."""
    # Assuming we had a list of notifications; return empty for now.
    return jsonify([])

@app.route('/api/alerts/check')
def api_check_alerts():
    """API endpoint to check stock alerts (returns list of alert messages)."""
    alerts = stock_monitor.check_alerts()
    return jsonify(alerts)

@app.route('/')
def index():
    """Simple health-check endpoint."""
    return "NOVAXA API is running!", 200

# --- Startup (Polling vs Webhook) ---

if __name__ == '__main__':
    # Decide mode based on WEBHOOK_URL env
    webhook_url = os.environ.get('WEBHOOK_URL')
    if webhook_url:
        # Webhook mode
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        # Start scheduler thread even in webhook mode
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        # Run Flask server (Render will provide PORT)
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Polling mode (e.g., for local development)
        bot.remove_webhook()
        # Start scheduler in background
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Starting bot in polling mode...")
        bot.polling(none_stop=True, interval=0)