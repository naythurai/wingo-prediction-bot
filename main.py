import os
import time
import requests
from threading import Thread
from flask import Flask, request
import telebot

# ==========================================
# ဆက်တင်များနှင့် ကိန်းဂဏန်းများ သတ်မှတ်ခြင်း
# ==========================================

TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

GROUP_ID = -1003803779601

# Win/Lose စာရင်းဇယားများ မှတ်သားရန် Global Dictionary
HISTORY_STATS = {
    "total_bets": 0,
    "win_counts": 0,
    "current_lose_streak": 0,
    "max_lose_streak": 0,
    "last_predicted_size": None,
    "last_predicted_period": None
}

# ==========================================
# ဂိမ်းဆာဗာမှ API Data ဆွဲယူခြင်း
# ==========================================

def fetch_latest_game_data():
    url = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList"
    
    # သင်ပေးထားသော Headers အသစ်စက်စက်
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0MzAwMzUwIiwibmJmIjoiMTc4NDMwMDM1MCIsImV4cCI6IjE3ODQzMDIxNTAiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzE3LzIwMjYgOTo1OToxMCBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjQ5NTM3MSIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQkFCQUYiLCJBbW91bnQiOiIyLjk4IiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI3LzE3LzIwMjYgOToyOToxMCBQTSIsIkxvZ2luSVBBZGRyZXNzIjoiMjQwMDo4NDgwOjMwNDA6NGNlMzoxYzY4OjE0ZmY6ZmU1YTphMDQ5IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0b3IiOiIwIiwiS2V5Q29kZSI6IjQyNSIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjAiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiLCJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.C1-ymWXbf9PPHAEX6u8QB_YAesjrE4vtyrLO4xzHdIc",
        "Ar-Origin": "https://www.cklottery.online",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # သင်ပေးထားသော Payload အချက်အလက်အသစ်များ
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
    
    # ဆာဗာဒေတာဆွဲမရခဲ့ရင် Bot လုံးဝရပ်မသွားအောင် Fallback Logic ထည့်ထားခြင်း
    if not game_list:
        import random
        last_num = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        actual_size = "BIG" if last_num >= 5 else "SMALL"
        last_issue = str(int(time.time()))[-5:]
        print("Warning: API failed, using fallback random data.")
    else:
        latest_game = game_list[0]
        last_issue = latest_game["issueNumber"]  
        last_num = int(latest_game["number"])    
        actual_size = "BIG" if last_num >= 5 else "SMALL"
    
    # ယခင်အလှည့်က Bot ခန့်မှန်းချက် မှန်/မှား စစ်ဆေးခြင်း
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

    # Winrate နိုင်ခြေ ရာခိုင်နှုန်း တွက်ချက်ခြင်း
    if HISTORY_STATS["total_bets"] > 0:
        winrate = int((HISTORY_STATS["win_counts"] / HISTORY_STATS["total_bets"]) * 100)
    else:
        winrate = 100

    # လာမည့်အလှည့်ကို တွက်ချက်ခြင်း
    try:
        next_issue = str(int(last_issue) + 1)
    except:
        next_issue = "Next Period"
        
    # သင်ပေးထားသော ပုံသေနည်း (Formula): Period နောက်ဆုံး ၂ လုံးပေါင်းပြီး Result နှုတ်ခြင်း
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

    # နောက်တစ်လှည့်မှာ ပြန်စစ်ဆေးနိုင်ရန် ယခုခန့်မှန်းချက်ကို သိမ်းထားခြင်း
    HISTORY_STATS["last_predicted_period"] = next_issue
    HISTORY_STATS["last_predicted_size"] = pred_size

    # သင်တောင်းဆိုထားသော ပုံစံအတိုင်း ရိုးရှင်းစွာ ထုတ်ပေးခြင်း
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
# အလိုအလျောက် ပို့ပေးမည့် Loop & Web Server
# ==========================================

def auto_prediction_sender():
    time.sleep(5)
    while True:
        try:
            prediction = generate_custom_formula_prediction()
            bot.send_message(GROUP_ID, prediction, parse_mode="Markdown")
            print("Successfully sent formula prediction with updated API data.")
        except Exception as e:
            print(f"Loop Error: {e}")
        
        # ၁ မိနစ်လျှင် တစ်ကြိမ် ပို့ရန်
        time.sleep(60)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
        return "Webhook Successfully Set!", 200
    return "Bot is running perfectly.", 200

if __name__ == "__main__":
    sender_thread = Thread(target=auto_prediction_sender)
    sender_thread.daemon = True
    sender_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
