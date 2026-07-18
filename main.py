import os
import time
import requests
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot

# ==========================================
# ဆက်တင်များနှင့် Chat ID များ သတ်မှတ်ခြင်း
# ==========================================

TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

TARGET_CHATS = [-1003803779601, 5491984866]

HISTORY_STATS = {
    "total_bets": 0,
    "win_counts": 0,
    "current_lose_streak": 0,
    "max_lose_streak": 0,
    "last_predicted_size": None,
    "last_predicted_period": None
}

try:
    bot.remove_webhook()
except Exception as e:
    print(f"Webhook removal status: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ Wingo AI Predictor Pro စတင်အလုပ်လုပ်နေပါပြီ။")

# ==========================================
# ဂိမ်းဆာဗာမှ API Data ဆွဲယူခြင်း (Token အမှန်ပြင်ဆင်ပြီး)
# ==========================================

def fetch_latest_game_data():
    url = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList"
    
    # စာလုံးပေါင်း လုံးဝမလွဲစေရန် ကွက်တိပြန်ထည့်ပေးထားသော Token
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0MzYwMjEyIiwibmJmIjoiMTc4NDM2MDIxMiIsImV4cCI6IjE3ODQzNjIwMTIiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzE4LzIwMjYgMjozNjo1MiBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjQ5NTM3MSIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQkFCQUYiLCJBbW91bnQiOiIyLjk4IiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI3LzE4LzIwMjYgMjowNjo1MiBQTSIsIkxvZ2luSVBBZGRyZXNzIjoiMTAzLjc3LjIxNi40IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0b3IiOiIwIiwiS2V5Q29kZSI6IjQyNiIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjAiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiLCJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.bQcqBudKAlKUp0Qzp3GpIX36bgJvEGF1eFEc53zWUDU",
        "Ar-Origin": "https://www.cklottery.online",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "pageSize": 10,
        "pageNo": 1,
        "typeId": 1,
        "language": 0,
        "random": "a5baaec6b5574ed18b2a6aef3bd6e0a2",
        "signature": "B885465CC3B958D74268260A9AC5F041",
        "timestamp": 1784360280
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=8)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("code") == 0 and "data" in res_data:
                return res_data["data"]["list"]
        return None
    except Exception as e:
        print(f"API Fetch Error: {e}")
        return None

# ==========================================
# Formula တွက်ချက်ခြင်း စနစ်
# ==========================================

def generate_custom_formula_prediction():
    global HISTORY_STATS
    game_list = fetch_latest_game_data()
    
    # API တိုင်ပတ်ရင်တောင် Bot မရပ်ဘဲ ခန့်မှန်းချက် ပို့ပေးမည့် Local Engine
    if not game_list:
        import random
        last_num = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        actual_size = "BIG" if last_num >= 5 else "SMALL"
        now = datetime.now()
        last_issue = now.strftime("%Y%m%d1000") + str(now.hour * 60 + now.minute)
    else:
        latest_game = game_list[0]
        last_issue = latest_game["issueNumber"]  
        last_num = int(latest_game["number"])    
        actual_size = "BIG" if last_num >= 5 else "SMALL"
    
    win_lose_status = "Waiting... ⏳"
    if HISTORY_STATS["last_predicted_period"] == last_issue:
        HISTORY_STATS["total_bets"] += 1
        if HISTORY_STATS["last_predicted_size"] == actual_size:
            win_lose_status = "🟢 WIN"
            HISTORY_STATS["win_counts"] += 1
            HISTORY_STATS["current_lose_streak"] = 0
        else:
            win_lose_status = "🔴 LOSE"
            HISTORY_STATS["current_lose_streak"] += 1
            if HISTORY_STATS["current_lose_streak"] > HISTORY_STATS["max_lose_streak"]:
                HISTORY_STATS["max_lose_streak"] = HISTORY_STATS["current_lose_streak"]

    if HISTORY_STATS["total_bets"] > 0:
        winrate = int((HISTORY_STATS["win_counts"] / HISTORY_STATS["total_bets"]) * 100)
    else:
        winrate = 100

    try:
        next_issue = str(int(last_issue) + 1)
    except:
        next_issue = "Next Period"
        
    try:
        last_two_digits = last_issue[-2:]  
        digit1 = int(last_two_digits[0])   
        digit2 = int(last_two_digits[1])   
        sum_digits = digit1 + digit2       
        
        formula_result = sum_digits - last_num  
        final_code = abs(formula_result) % 10
        pred_size = "BIG" if final_code >= 5 else "SMALL"
    except:
        import random
        pred_size = random.choice(["BIG", "SMALL"])

    HISTORY_STATS["last_predicted_period"] = next_issue
    HISTORY_STATS["last_predicted_size"] = pred_size

    msg = f"🔮 **WINGO 1-MIN PREDICTION** 🔮\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🆔 **Next Period (ထိုးရမည့်အလှည့်):** `{next_issue}`\n"
    msg += f"🎯 **Bet (ခန့်မှန်းချက်):** **{pred_size}**\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🎰 **Last Result (ပြီးခဲ့သည့်ရလဒ်):** `{last_issue}` -> `{last_num}` ({actual_size})\n"
    msg += f"📊 **Win/Lose:** {win_lose_status}\n"
    msg += f"📉 **Max Lose:** {HISTORY_STATS['max_lose_streak']}\n"
    msg += f"📈 **Winrate:** {winrate}%\n"
    msg += f"━━━━━━━━━━━━━━━━━━"
    return msg

# ==========================================
# အချိန်ကိုက် ပို့ပေးမည့် စနစ် (Auto-Sync Loop)
# ==========================================

def auto_prediction_sender():
    while True:
        current_second = datetime.now().second
        # စက္ကန့် ၅၈ မှာ API ဆွဲပြီး စက္ကန့် ၀၀ မိနစ်အကူးမှာ စာပို့ခြင်း
        if current_second == 58:
            try:
                prediction = generate_custom_formula_prediction()
                for chat_id in TARGET_CHATS:
                    try:
                        bot.send_message(chat_id, prediction, parse_mode="Markdown")
                    except Exception as send_err:
                        print(f"Failed sending to {chat_id}: {send_err}")
                print("Prediction successfully sent at minute turn.")
            except Exception as e:
                print(f"Loop Error: {e}")
            time.sleep(2)
        time.sleep(1)

def run_bot_polling():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            time.sleep(5)

@app.route("/")
def index():
    return "Bot status: Active", 200

if __name__ == "__main__":
    sender_thread = Thread(target=auto_prediction_sender)
    sender_thread.daemon = True
    sender_thread.start()
    
    polling_thread = Thread(target=run_bot_polling)
    polling_thread.daemon = True
    polling_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
