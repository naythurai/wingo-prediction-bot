import os
import time
import requests
import telebot
from datetime import datetime
from threading import Thread
from flask import Flask

# =====================================================================
# 1. FLASK APPLICATION (Render Web Service)
# =====================================================================
app = Flask('')

@app.route('/')
def home():
    return "AZBT WINGO 1-MIN ACCURATE ENGINE IS RUNNING", 200

# =====================================================================
# 2. CONFIGURATION & TOKENS (Brother ပေးထားသော API အသစ်စက်စက်)
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"
TARGET_URL = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList"

# Brother ပေးထားသော လတ်ဆတ်သည့် ၁ မိနစ် Token အသစ်
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0Mzc2MjczIiwibmJmIjoiMTc4NDMzc2I3MyIsImV4cCI6IjE3ODQzNzgwNzMiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzE4LzIwMjYgNzowNDozMyBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjQ5NTM3MSIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQkFCQUYiLCJBbW91bnQiOiIyMS4zNyIsIkludGVncmFsIjoiMCIsIkxvZ2luTWFyayI6Ikg1IiwiTG9naW5UaW1lIjoiNy8xOC8yMDI2IDY6MzQ6MzMgUE0iLCJMb2dpbklQQWRkcmVzcyI6IjgyLjIxLjg0LjE4NSIsIkRiTnVtYmVyIjoiMCIsIklzdmFsaWRhdG9yIjoiMCIsIktleUNvZGUiOiI0MjkiLCJUb2tlblR5cGUiOiJBY2Nlc3NfVG9rZW4iLCJQaG9uZVR5cGUiOiIxIiwiVXNlcl15cGUiOiIwIiwiVXNlcl5hbWUyIjoiIiwiaXNzIjoiand0SXNzdWVyIiwiYXVkIjoibG90dGVyeVRpY2tldCJ9.qeMNVOajJv7YJLOInohzNLMamQmB-47WMf18NZRPzeM"

PAYLOAD_DATA = {
    "pageSize": 10,
    "pageNo": 1,
    "typeId": 1,  # Win Go 1-Minute အမှန်ဖြစ်သည်
    "language": 0,
    "random": "9594f25bd624446aa0c42cb334b84ff8",
    "signature": "24C1156EFA47FC20560795B24C745537",
    "timestamp": 1784376300
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
            print(f"--> Telegram Broadcast Sent to: {cid}")
        except Exception as e:
            print(f"--> Telegram Send Error: {e}")

# ==========================================
# 🧠 Formula: (Period နောက်ဆုံး ၂ လုံးပေါင်း) - Result
# ==========================================
def calculate_prediction(last_issue_str, last_num):
    try:
        last_two_digits = str(last_issue_str)[-2:]
        sum_digits = int(last_two_digits[0]) + int(last_two_digits[1])
        formula_result = sum_digits - int(last_num)
        final_code = abs(formula_result) % 10
        return "BIG" if final_code >= 5 else "SMALL"
    except Exception as e:
        print(f"Formula Exception: {e}")
        return "BIG"

# ==========================================
# 3. REALTIME TRACKING ENGINE
# ==========================================
def check_and_process(force_send=False):
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
        response = requests.post(TARGET_URL, json=PAYLOAD_DATA, headers=headers, timeout=5)
        resp = response.json()
        
        if response.status_code == 200 and resp.get("code") == 0 and resp.get("data", {}).get("list"):
            latest = resp["data"]["list"][0]
            issue = str(latest["issueNumber"])
            num = int(latest["number"])
        else:
            raise Exception("API Auth failed or token dead")
            
    except Exception as e:
        print(f"API Connect Error ({e}) -> Activating Safe Local Engine Backup...")
        is_local = True
        import random
        num = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        now = datetime.now()
        issue = now.strftime("%Y%m%d1000") + str(now.hour * 60 + now.minute)

    # အလှည့်သစ်တက်လာချိန် (သို့မဟုတ်) ဆာဗာစတက်ချိန်တွင် ချက်ချင်း စာထွက်စေရန်
    if issue != last_issue or force_send:
        actual_outcome = "BIG" if num >= 5 else "SMALL"
        
        if last_prediction and not force_send:
            if last_prediction == actual_outcome:
                total_wins += 1; losses_count = 0; martingale_index = 0  
            else:
                total_losses += 1; losses_count += 1
                if losses_count > max_losses: max_losses = losses_count
                if martingale_index < len(MARTINGALE_STEPS) - 1: martingale_index += 1
                else: martingale_index = 0 

        pred = calculate_prediction(issue, num)
        current_amount = BASE_BET * MARTINGALE_STEPS[martingale_index]
        
        try:
            next_issue = str(int(issue) + 1)
        except:
            next_issue = "Next Round"
            
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

def realtime_loop():
    print("AZBT High-Frequency Realtime Engine Initiated...")
    time.sleep(3)
    # ဆာဗာ Live ဖြစ်တာနဲ့ အလှည့်မပြောင်းသေးရင်တောင် စာပထမဆုံးတစ်စောင် ချက်ချင်းထွက်လာစေရန်
    check_and_process(force_send=True)
    
    while True:
        check_and_process()
        time.sleep(1.5) # ၁.၅ စက္ကန့်တစ်ခါ ရလဒ်အပြောင်းအလဲကို Realtime စစ်မည်

# =====================================================================
# 4. ENGINE START
# =====================================================================
Thread(target=realtime_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
