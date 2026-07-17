import os
import time
import requests
from threading import Thread
from flask import Flask
import telebot

# ==========================================
# ဆက်တင်များနှင့် ကိန်းဂဏန်းများ သတ်မှတ်ခြင်း
# ==========================================

# သင်ပေးထားသော Token နှင့် Group ID အမှန်များဖြစ်ကြပါသည်
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

GROUP_ID = -1003803779601

HISTORY_STATS = {
    "total_bets": 0,
    "win_counts": 0,
    "current_lose_streak": 0,
    "max_lose_streak": 0,
    "last_predicted_size": None,
    "last_predicted_period": None
}

# Webhook ကို လုံးဝပိတ်ပြီး Polling စနစ်သို့ ပြောင်းရန် ဖျက်သိမ်းခြင်း
try:
    bot.remove_webhook()
except Exception as e:
    print(f"Webhook removal status: {e}")

# ==========================================
# ဂိမ်းဆာဗာမှ API Data ဆွဲယူခြင်း
# ==========================================

def fetch_latest_game_data():
    url = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList"
    
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0MzAwMzUwIiwibmJmIjoiMTc4NDMwMDM1MCIsImV4cCI6IjE3ODQzMDIxNTAiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzE3LzIwMjYgOTo1OToxMCBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjQ5NTM3MSIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQkFCQUYiLCJBbW91bnQiOiIyLjk4IiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI3LzE3LzIwMjYgOToyOToxMCBQTSIsIkxvZ2luSVBBZGRyZXNzIjoiMjQwMDo4NDgwOjMwNDA6NGNlMzoxYzY4OjE0ZmY6ZmU1YTphMDQ5IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0b3IiOiIwIiwiS2V5Q29kZSI6IjQyNSIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjAiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiLCJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.C1-ymWXbf9PPHAEX6u8QB_YAesjrE4vtyrLO4xzHdIc",
        "Ar-Origin": "https://www.cklottery.online",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "pageSize": 10,
        "pageNo": 1,
        "typeId": 1,
        "language": 0,
        "random": "6cea9e6f240e45d69ace907d6756ad79",
        "signature": "912609C0C714A114DD7FB311BCEB5B7D",
        "timestamp": 1784300353
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("code") == 0 and "data" in res_data:
                return res_data["data"]["list"]
        return None
    except Exception as e:
        print(f"API Fetch Error: {e}")
        return None

# ==========================================
# Formula တွက်ချက်ခြင်းနှင့် စာသားထုတ်ခြင်း
# ==========================================

def generate_custom_formula_prediction():
    global HISTORY_STATS
    game_list = fetch_latest_game_data()
    
    if not game_list:
        import random
        last_num = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        actual_size = "BIG" if last_num >= 5 else "SMALL"
        last_issue = str(int(time.time()))[-5:]
    else:
        latest_game = game_list[0]
        last_issue = latest_game["issueNumber"]  
        last_num = int(latest_game["number"])    
        actual_size = "BIG" if last_num >= 5 else "SMALL"
    
    win_lose_status = "Waiting..."
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
    msg += f"🆔 **Period:** `{next_issue}`\n"
    msg += f"🎰 **Result:** `{last_num}` ({actual_size})\n"
    msg += f"🎯 **Bet:** **{pred_size}**\n"
    msg += f"📊 **Win/Lose:** {win_lose_status}\n"
    msg += f"📉 **Max Lose:** {HISTORY_STATS['max_lose_streak']}\n"
    msg += f"📈 **Winrate:** {winrate}%\n"
    msg += f"━━━━━━━━━━━━━━━━━━"
    return msg

# ==========================================
# အလိုအလျောက် ပို့ပေးမည့် Loop
# ==========================================

def auto_prediction_sender():
    time.sleep(5)
    while True:
        try:
            prediction = generate_custom_formula_prediction()
            bot.send_message(GROUP_ID, prediction, parse_mode="Markdown")
            print("Prediction sent to group successfully via Polling Thread.")
        except Exception as e:
            print(f"Loop Error: {e}")
        
        time.sleep(60)

# Render အိပ်မပျော်အောင် dummy server ထားခြင်း
@app.route("/")
def index():
    return "Bot is running on Polling mode.", 200

if __name__ == "__main__":
    # စာအလိုအလျောက်ပို့မည့် Thread ကို စတင်ခြင်း
    sender_thread = Thread(target=auto_prediction_sender)
    sender_thread.daemon = True
    sender_thread.start()
    
    # Render Port ငြိစွန်းမှုမရှိစေရန် Flask ကို background တွင် run ထားခြင်း
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
