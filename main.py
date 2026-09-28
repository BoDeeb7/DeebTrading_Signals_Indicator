import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# جلب البيانات من البيئة للحفاظ على أمان المفاتيح
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_signal(data):
    """صياغة وإرسال رسالة التوصية إلى التليجرام"""
    symbol = data.get("symbol", "N/A")
    action = data.get("action", "ALERT").upper()
    price = data.get("price", "N/A")
    sl = data.get("sl", "N/A")
    tp1 = data.get("tp1", "N/A")
    tp2 = data.get("tp2", "N/A")

    # تحديد الشعار واللون بناءً على نوع الصفقة
    icon = "🔵 BUY SIGNAL" if "BUY" in action else "🔴 SELL SIGNAL"

    message = (
        f"🚨 *إشارة جديدة من المؤشر ({symbol})*\n\n"
        f"📊 *نوع الصفقة:* {icon}\n"
        f"🎯 *سعر الدخول:* `{price}`\n"
        f"🛑 *وقف الخسارة (SL):* `{sl}`\n"
        f"🎯 *الهدف الأول (TP1):* `{tp1}`\n"
        f"🎯 *الهدف الثاني (TP2):* `{tp2}`\n\n"
        f"⏰ *التوقيت:* تلقائي عبر TradingView Webhook"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or request.form.to_dict()
    if data:
        print(f"Received Webhook Data: {data}")
        send_telegram_signal(data)
        return jsonify({"status": "success", "message": "Signal sent to Telegram"}), 200
    return jsonify({"status": "error", "message": "No data received"}), 400

@app.route('/', methods=['GET'])
def health_check():
    return "TradingView Webhook Server is Running Successfully!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))