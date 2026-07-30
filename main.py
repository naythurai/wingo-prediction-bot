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
    return "AZBT CUSTOM-LOGIC ENGINE ACTIVE", 200

# =====================================================================
# 2. CONFIGURATION & TOKENS
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"

TARGET_URL = "https://api.bigwinqaz.com/api/webapi/GetNoaverageEmerdList"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg1MzA5MzAyIiwibmJmIjoiMTc4NTMwOTMwMiIsImV4cCI6IjE3ODUzMTExMDIiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzI5LzIwMjYgMjoxNTowMiBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjYwNTYzMiIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQ0FLWk4iLCJBbW91bnQiOiI0LjAwIiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI3LzI5LzIwMjYgMTo0NTowMiBQTSIsIkxvZ2luSVBBZGRyZXNzIjoiNDUuMTk2LjE2LjIzNyIsImRiTnVtYmVyIjoiMCIsIklzdmFsaWRhdG9yIjoiMCIsIktleUNvZGUiOiIxMzciLCJUb2tlblR5cGUiOiJBY2Nlc3NfVG9rZW4iLCJQaG9uZVR5cGUiOiIxIiwiVXNlciJUeXBlIjoiMCIsIlVzZXJOYW1lMiI6IiIsImlzcyI6nd0SXNzdWVyIiwiYXVkIjoibG90dGVyeVRpY2tldCJ9.zJh3XG2q9a40dCQ3z1tm8oUvvh1iVgeNE93RyIAP6CQ"

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
# 3. CUSTOM PREDICTION LOGIC (Period Last Digit 0 or 5 Check)
# ==========================================
def calculate_custom_prediction(last_period_str):
    try:
        # Next Period နံပါတ်ကို တွက်ချက်ခြင်း
        next_issue_num = int(last_period_str) + 1
        next_period_str = str(next_issue_num)

        # Period နောက်ဆုံးဂဏန်းကို ယူခြင်း
        last_digit = int(next_period_str[-1])

        # Period နောက်ဆုံးဂဏန်း 0 သို့မဟုတ် 5 ဖြစ်မှသာ Predation ထုတ်မည် (ကျန်သည်များကို WAIT စေမည်)
        if last_digit == 0 or last_digit == 5:
            # 0 ဆိုရင် Small, 5 ဆိုရင် Big (သို့မဟုတ် လိုအပ်သလို သတ်မှတ်ချက်အတိုင်း 0-4 Small, 5-9 Big)
            if last_digit in [0, 1, 2, 3, 4]:
                target_group = "SMALL"
                color = "🟢"
            else:
                target_group = "BIG"
                color = "🔴"
            return target_group, color, last_digit
        else:
            return "WAIT", "⚪", last_digit
            
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
        "random": "bfb7722196414c308822378d5324d90e",
        "signature": "78F869690E499C1E3555D1D79306AF20",
        "timestamp": int(time.time())
    }
    
    try:
        response = session.post(TARGET_URL, json=payload, timeout=5)
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

                    # ⚡ Custom Prediction Logic (Period နောက်ဆုံးနံပါတ် 0 သို့မဟုတ် 5 မှသာ Signal ထုတ်မည်)
                    final_pred, pred_color, last_digit = calculate_custom_prediction(current_issue)

                    total_actual_bets = actual_bet_wins + actual_bet_losses
                    win_rate = (actual_bet_wins / total_actual_bets * 100) if total_actual_bets > 0 else 100.0
                    
                    server_time = resp.get("serviceNowTime", "").split(' ')[-1]
                    
                    if final_pred == "WAIT":
                        display_pred = "🛑 WAIT (Period Digit: " + str(last_digit) + ")"
                        last_prediction = "WAIT"
                        current_amount = BASE_BET
                    else:
                        display_pred = f"**{final_pred}** {pred_color} (Period Digit: {last_digit})"
                        last_prediction = final_pred
                        current_amount = BASE_BET * MARTINGALE_STEPS[martingale_index]

                    if is_win_event:
                        header_banner = "🏆🏆🏆 **WIN RESULT** 🏆🏆🏆"
                    else:
                        header_banner = "⚡ **AZBT CUSTOM-LOGIC ENGINE** ⚡"

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
    print("AZBT Custom-Logic Engine Active...")
    while True:
        check_and_process()
        time.sleep(1)

# =====================================================================
# 5. RUN
# =====================================================================
Thread(target=realtime_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
