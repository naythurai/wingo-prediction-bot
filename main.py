import os
import time
import requests
import telebot
from threading import Thread
from flask import Flask

# =====================================================================
# 1. FLASK APPLICATION
# =====================================================================
app = Flask('')

@app.route('/')
def home():
    return "AZBT DIGITAL-SUM ENGINE ACTIVE", 200

# =====================================================================
# 2. CONFIGURATION & TOKENS
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"

TARGET_URL = "https://api.bigwinqaz.com/api/webapi/GetNoaverageEmerdList"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0NzY2MTQ1IiwibmJmIjoiMTc4NDc2NjE0NSIsImV4cCI6IjE3ODQ3Njc5NDUiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzIzLzIwMjYgNzoyMjoyNSBBTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjYwNTYzMiIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQ0FLWk4iLCJBbW91bnQiOiI2LjAwIiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI3LzIzLzIwMjYgNjo1MjoyNSBBTSIsImxvZ2luSVBBZGRyZXNzIjoiODIuMjEuODQuMTY3IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0b3IiOiIwIiwiS2V5Q29kZSI6IjEwOCIsIlRva2VuVHlwZSI6IjEiLCJQaG9uZVR5cGUiOiIxIiwiVXNlclR5cGUiOiIwIiwiVXNlck5hbWUyIjoiIiwipc3MiOiJqd3RJc3N1ZXIiLCJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.Qf_n3paiDbTmfn8wFQC76zWU6stRLm9MR1mVH4C8zO8"

bot = telebot.TeleBot(TOKEN)

# ⚡ High-Speed HTTP Session
session = requests.Session()
session.headers.update({
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Authorization": AUTH_TOKEN,
    "Ar-Origin": "https://www.bigwingame.cc",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

BASE_BET = 100
MARTINGALE_STEPS = [1, 3, 8, 24, 72, 216, 648, 1944, 5832]
martingale_index = 0

last_checked_issue = ""
consecutive_losses = 0
actual_current_losses = 0
actual_max_losses = 0
actual_bet_wins = 0
actual_bet_losses = 0
last_prediction = ""

def send_msg(text):
    for cid in [CHAT_ID, GROUP_ID]:
        try: 
            bot.send_message(cid, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Send Error: {e}")

# ==========================================
# 3. DIGITAL SUM PREDICTION LOGIC
# ==========================================
def single_digit_sum(n):
    while n >= 10:
        n = sum(int(digit) for digit in str(n))
    return n

def calculate_digital_sum_prediction(last_period_str):
    try:
        # 1. လာမည့်မိနစ်ကို တွက်ချက်ခြင်း
        current_minute = time.localtime().tm_min
        s_min = single_digit_sum(current_minute)

        # 2. ပြီးခဲ့တဲ့ Period နံပါတ်၏ နောက်ဆုံး ၂ လုံးကို တွက်ချက်ခြင်း
        last_two_digits = int(last_period_str[-2:])
        s_per = single_digit_sum(last_two_digits)

        # 3. ရလဒ်ဖော်ထုတ်ခြင်း
        tot = single_digit_sum(s_min + s_per)

        target_group = "BIG" if tot in [5, 6, 7, 8, 9] else "SMALL"
        color = "🔴" if tot % 2 == 0 else "🟢"

        return target_group, color, tot
    except Exception as e:
        return "WAIT", "⚪", 0

# ==========================================
# 4. FAST ENGINE CORE
# ==========================================
def check_and_process():
    global last_checked_issue, consecutive_losses
    global actual_current_losses, actual_max_losses
    global actual_bet_wins, actual_bet_losses
    global last_prediction, martingale_index
    
    payload = {
        "pageSize": 10,
        "pageNo": 1,
        "typeId": 30,
        "language": 7,
        "random": "01af5df2589a44068d5f6c4afd9c7909",
        "signature": "4E92D41CCD35B460214225B802C38496",
        "timestamp": int(time.time())
    }
    
    try:
        response = session.post(TARGET_URL, json=payload, timeout=3)
        resp = response.json()
        
        if response.status_code == 200 and resp.get("code") == 0 and resp.get("data"):
            result_list = resp["data"].get("list", [])
            if len(result_list) > 0:
                # အသစ်ဆုံး ထွက်ထားသော ရလဒ်ကို ယူခြင်း
                latest_item = result_list[0]
                current_issue = latest_item.get("issueNumber")
                
                if current_issue != last_checked_issue:
                    current_num = int(latest_item.get("number"))
                    actual_outcome = "BIG" if current_num >= 5 else "SMALL"
                    is_win_event = False

                    if last_prediction and last_prediction != "WAIT":
                        if last_prediction == actual_outcome:
                            actual_bet_wins += 1
                            consecutive_losses = 0
                            actual_current_losses = 0
                            martingale_index = 0
                            status_text = "🟢 WIN ✅"
                            is_win_event = True
                        else:
                            actual_bet_losses += 1
                            consecutive_losses += 1
                            actual_current_losses += 1
                            
                            if martingale_index < len(MARTINGALE_STEPS) - 1:
                                martingale_index += 1
                            
                            if actual_current_losses > actual_max_losses:
                                actual_max_losses = actual_current_losses
                            
                            status_text = f"🔴 LOSE ❌ ({consecutive_losses})"
                    else:
                        status_text = "⚪ SKIPPED"

                    # ⚡ Digital Sum Logic ကို ဤနေရာတွင် သုံးမည် (Actual IssueNumber ကို ထည့်သွင်းတွက်ချက်သည်)
                    raw_pred, pred_color, total_sum = calculate_digital_sum_prediction(current_issue)
                    
                    final_pred = raw_pred
                    reversion_tag = ""
                    
                    if consecutive_losses >= 2 and raw_pred != "WAIT":
                        final_pred = "SMALL" if raw_pred == "BIG" else "BIG"
                        reversion_tag = " 🔄 (REVERSED)"

                    total_actual_bets = actual_bet_wins + actual_bet_losses
                    win_rate = (actual_bet_wins / total_actual_bets * 100) if total_actual_bets > 0 else 100.0
                    
                    server_time = resp.get("serviceNowTime", "").split(' ')[-1]
                    
                    if final_pred == "WAIT":
                        display_pred = "🛑 WAIT"
                        last_prediction = "WAIT"
                        current_amount = BASE_BET
                    else:
                        display_pred = f"**{final_pred}** {pred_color} (Sum: {total_sum}){reversion_tag}"
                        last_prediction = final_pred
                        current_amount = BASE_BET * MARTINGALE_STEPS[martingale_index]

                    if is_win_event:
                        header_banner = "🏆🏆🏆 **WIN RESULT** 🏆🏆🏆"
                    else:
                        header_banner = "⚡ **AZBT DIGITAL-SUM ENGINE** ⚡"

                    msg = (f"{header_banner}\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n"
                           f"🎯 **NEXT SIGNAL:** {display_pred}\n"
                           f"🎰 **LAST ISSUE:** `{current_issue}`\n"
                           f"🎲 **LAST RESULT:** `{current_num}` ({actual_outcome})\n"
                           f"📊 **STATUS:** {status_text}\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n"
                           f"💵 **BET:** `{current_amount:,} MMK` (Step {martingale_index + 1})\n"
                           f"📈 **WIN RATE:** `{win_rate:.1f}%` (W: `{actual_bet_wins}` | L: `{actual_bet_losses}`)\n"
                           f"📉 **LOSS:** Max `{actual_max_losses}` | Current `{actual_current_losses}`\n"
                           f"⏱️ **TIME:** `{server_time}`\n"
                           f"━━━━━━━━━━━━━━━━━━━━")
                    
                    send_msg(msg)
                    last_checked_issue = current_issue

    except Exception as e:
        print(f"Error: {e}")

def realtime_loop():
    print("AZBT Digital-Sum Engine with GetNoaverageEmerdList Active...")
    while True:
        check_and_process()
        time.sleep(0.5)

# =====================================================================
# 5. RUN
# =====================================================================
Thread(target=realtime_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
