"""
Backend API for NOVAXA Dashboard and Telegram Bot
Provides endpoints for stock data and project status
"""

from flask import Flask, jsonify
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='novaxa_api.log'
)
logger = logging.getLogger(__name__)

# Init Flask
app = Flask(__name__)

# Dummy projects (ίδια με το bot για συμβατότητα)
projects = {
    "bidprice": {
        "name": "BidPrice",
        "status": "Active",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Πλατφόρμα δημοπρασιών προϊόντων",
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
        "metrics": {
            "messages_sent": 156,
            "recipients": 42,
            "progress": 60
        }
    }
}

# Route: root
@app.route("/")
def index():
    return "NOVAXA API is running"

# Route: project status
@app.route("/api/projects", methods=["GET"])
def get_projects():
    return jsonify({"projects": projects})

# Run
if __name__ == "__main__":
    logger.info("Starting NOVAXA API backend...")
    app.run(host="0.0.0.0", port=5000)
