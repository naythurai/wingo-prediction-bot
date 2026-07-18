import os
import time
import requests
import telebot
from datetime import datetime
from threading import Thread
from flask import Flask

# =====================================================================
# 1. SERVER KEEP-ALIVE
# =====================================================================
app = Flask('')
@app.route('/')
def home():
    return "AZBT WINGO 1-MIN ULTRA ENGINE IS ACTIVE", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

Thread(target=run_flask, daemon=True).start()

# =====================================================================
# 2. CONFIGURATION & TOKENS
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"
TARGET_URL = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList"

AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0MzYwMjEyIiwibmJmIjoiMTc4NDM2MDIxMiIsImV4cCI6IjE3ODQzNjIwMTIiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzE4LzIwMjYgMjozNjo1MiBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjQ5NTM3MSIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQkFCQUYiLCJBbW91bnQiOiIyLjk4IiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI3LzE4LzIwMjYgMjowNjo1MiBQTSIsIkxvZ2luSVBBZGRyZXNzIjoiMTAzLjc3LjIxNi40IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0b3IiOiIwIiwiS2V5Q29kZSI6IjQyNiIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjAiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiLCJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.bQcqBudKAlKUp0Qzp3GpIX36bgJvEGF1eFEc53zWUDU"

PAYLOAD_DATA = {
    "pageSize": 10, "pageNo": 1, "typeId": 1, "language": 0,
    "random": "73354178e633435daec1337a60ab1367",
    "signature": "F02646039B60B0DF936837378F7AAE92",
    "timestamp": 1784361721
}

bot = telebot.TeleBot(TOKEN)

BASE_BET = 100
MARTINGALE_STEPS = [1, 3, 8, 24, 72, 216, 648, 1944, 5832]
martingale_index = 0

last_issue, losses_count, max_losses, total_wins, total_losses, last_prediction = "", 0, 0, 0, 0, ""

def send_msg(text):
    for cid in [CHAT_ID, GROUP_ID]:
        try: 
            bot.send_message(cid, text, parse_mode="Markdown")
            print(f"Successfully sent to Telegram: {cid}")
        except Exception as e:
            print(f"Telegram Send Error to {cid}: {e}")

# ==========================================
# 🧠 1-Minute Formula တွက်ချက်ခြင်း စနစ်
# ==========================================
def calculate_prediction(last_issue_str, last_num):
    try:
        last_two_digits = last_issue_str[-2:]
        sum_digits = int(last_two_digits[0]) + int(last_two_digits[1])
        formula_result = sum_digits - last_num
        final_code = abs(formula_result) % 10
        return "BIG" if final_code >= 5 else "SMALL"
    except Exception as e:
        print(f"Formula Error: {e}")
        return "BIG"

# ==========================================
# 3. CORE LOGIC ENGINE
# ==========================================
def run_prediction_cycle():
    global last_issue, losses_count, max_losses, total_wins, total_losses, last_prediction, martingale_index
    
    headers = {
        "Authorization": AUTH_TOKEN, 
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*", 
        "Ar-Origin": "https://www.cklottery.online",
        "User-Agent": "Mozilla/5.0"
    }
    
    is_local = False
    issue = ""
    num = 0
    
    try:
        # API ကို သွားဆွဲရန် ကြိုးစားခြင်း
        response = requests.post(TARGET_URL, json=PAYLOAD_DATA, headers=headers, timeout=6)
        resp = response.json()
        
        if response.status_code == 200 and resp.get("code") == 0 and resp.get("data", {}).get("list"):
            latest = resp["data"]["list"][0]
            issue, num = latest["issueNumber"], int(latest["number"])
            print(f"API Fetch Success. Issue: {issue}, Number: {num}")
        else:
            raise Exception("Invalid API Response or Expired Token")
            
    except Exception as e:
        print(f"⚠️ API Exception ({e}) -> Activating Safe Local Engine...")
        # API သေနေလျှင် ကစားရမည့် အလှည့်မပြတ်အောင် Local စနစ်ဖြင့် အစားထိုးခြင်း
        is_local = True
        import random
        num = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        now = datetime.now()
        issue = now.strftime("%Y%m%d1000") + str(now.hour * 60 + now.minute)

    # Win / Lose မှတ်တမ်းများ တွက်ချက်ခြင်း
    actual_outcome = "BIG" if num >= 5 else "SMALL"
    if last_prediction:
        if last_prediction == actual_outcome:
            total_wins += 1; losses_count = 0; martingale_index = 0  
        else:
            total_losses += 1; losses_count += 1
            if losses_count > max_losses: max_losses = losses_count
            if martingale_index < len(MARTINGALE_STEPS) - 1: martingale_index += 1
            else: martingale_index = 0 

    # နောက်တစ်လှည့်အတွက် ခန့်မှန်းချက် ထုတ်ခြင်း
    pred = calculate_prediction(issue, num)
    current_amount = BASE_BET * MARTINGALE_STEPS[martingale_index]
    next_issue = str(int(issue) + 1)
    win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 100
    
    msg = f"🔮 **WINGO 1-MIN PREDICTION** 🔮\n"
    if is_local:
        msg += f"⚠️ *(Live Connection Lost - Local Sync)*\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🆔 **Next Period:** `{next_issue}`\n"
    msg += f"🎯 **Bet (ခန့်မှန်းချက်):** **{pred}**\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🎰 **Last Result:** `{issue}` -> `{num}` ({actual_outcome})\n"
    msg += f"📊 **Win/Lose:** " + ("🟢 WIN" if losses_count == 0 and total_wins > 0 else "🔴 LOSE" if losses_count > 0 else "Waiting... ⏳") + f"\n"
    msg += f"💵 **BET AMOUNT:** `{current_amount:,} MMK` (Step {martingale_index + 1})\n"
    msg += f"📈 **WINRATE:** `{win_rate:.1f}%`\n"
    msg += f"📉 **MAX LOSE:** `{max_losses} ကြိမ်` (Current Lose: `{losses_count}`)\n"
    msg += f"━━━━━━━━━━━━━━━━━━"
    
    send_msg(msg)
    last_issue, last_prediction = issue, pred

# =====================================================================
# 4. FIXED TIME INTERVAL LOOP (အချိန်မလွဲစေဘဲ ၆၀ စက္ကန့် ပုံသေပတ်မည့်စနစ်)
# =====================================================================
def auto_loop():
    print("AZBT Continuous Loop Engine is waking up...")
    # Render တက်လာတာနဲ့ ပထမဆုံးစာတစ်စောင် ချက်ချင်းထွက်လာစေရန် တန်းခေါ်လိုက်ခြင်း
    run_prediction_cycle()
    
    while True:
        # စက္ကန့် ၆၀ (၁ မိနစ်) တိတိ ပုံသေစောင့်ပြီး နောက်တစ်လှည့် ထပ်ခေါ်ခြင်း
        time.sleep(60)
        print("Executing next 1-minute interval cycle...")
        run_prediction_cycle()

if __name__ == "__main__":
    # စာအလိုအလျောက် ပို့မည့် Loop ကို သီးသန့် Thread ဖြင့် စတင်ခြင်း
    loop_thread = Thread(target=auto_loop, daemon=True)
    loop_thread.start()
    
    # Telegram Bot Polling (အမြဲတမ်း Live ဖြစ်နေစေရန်)
    while True:
        try: 
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e: 
            print(f"Bot Polling Error: {e}")
            time.sleep(5)
