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
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg1MzA5MzAyIiwibmJmIjoiMTc4FSB0MjkzMDIiLCJleHAiOiIxNzg1MzExMDIiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzI5LzIwMjYgMjoxNTowMiBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjYwNTYzMiIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQ0FLWk4iLCJBbW91bnQiOiI0LjAwIiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI3LzI5LzIwMjYgMTo0NTowMiBQTSIsImxvZ2luSVBBZGRyZXNzIjoiNDUuMTk2LjE2LjIzNyIsImRiTnVtYmVyIjoiMCIsIklzdmFsaWRhdG9yIjoiMCIsIktleUNvZGUiOiIxMzciLCJUb2tlblR5cGUiOiJBY2Nlc3NfVG9rZW4iLCJQaG9uZVR5cGUiOiIxIiwiVXNlciJUeXBlIjoiMCIsIlVzZXJOYW1lMiI6IiIsImlzcyI6nd0SXNzdWVyIiwiYXVkIjoibG90dGVyeVRpY2tldCJ9.zJh3XG2q9a40dCQ3z1tm8oUvvh1iVgeNE93RyIAP6CQ"

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

# 🔄 Trend Analysis Memory & History
recent_outcomes = []

def send_msg(text):
    for cid in [CHAT_ID, GROUP_ID]:
        try: 
            bot.send_message(cid, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Send Error: {e}")

# ==========================================
# 3. CUSTOM PREDICTION LOGIC & STABLE TREND ANALYZER
# ==========================================
def calculate_custom_prediction(last_period_str, outcome_history):
    try:
        next_issue_num = int(last_period_str) + 1
        next_period_str = str(next_issue_num)
        last_digit = int(next_period_str[-1])

        # 1. Period နောက်ဆုံးဂဏန်း 0 သို့မဟုတ် 5 ဖြစ်ပါက
        if last_digit == 0 or last_digit == 5:
            if last_digit in [0, 1, 2, 3, 4]:
                target_group = "SMALL"
                color = "🟢"
            else:
                target_group = "BIG"
                color = "🔴"
            return target_group, color, last_digit, "PERIOD_DIGIT"

        # 2. Trend ငြိမ်မည့်အချိန် (Stable Trend) ကို ရှာဖွေပြီး ခန့်မှန်းခြင်း
        if len(outcome_history) >= 6:
            last_few = outcome_history[-6:]
            
            # Trend ငြိမ်ခြင်း (Streak - နောက်ဆုံး ၃ ခု တူနေခြင်း)
            all_same_recent = all(x == last_few[-1] for x in last_few[-3:])
            if all_same_recent:
                stable_trend_target = last_few[-1]
                color = "🔴" if stable_trend_target == "BIG" else "🟢"
                return stable_trend_target, color, last_digit, f"STABLE_TREND ({stable_trend_target} Streak)"
            
            # Ping-Pong Trend ငြိမ်ခြင်း (တစ်လှည့်စီ ထွက်နေခြင်း)
            is_ping_pong = (last_few[-1] != last_few[-2]) and (last_few[-2] != last_few[-3]) and (last_few[-3] != last_few[-4])
            if is_ping_pong:
                anti_trend_target = "SMALL" if last_few[-1] == "BIG" else "BIG"
                color = "🔴" if anti_trend_target == "BIG" else "🟢"
                return anti_trend_target, color, last_digit, "PING_PONG_TREND"

        return "WAIT", "⚪", last_digit, "WAIT_UNSTABLE"
            
    except Exception as e:
        return "WAIT", "⚪", 0, "ERROR"

# ==========================================
# 4. FAST ENGINE CORE
# ==========================================
def check_and_process():
    global last_checked_issue, consecutive_losses
    global actual_current_losses, actual_max_losses
    global actual_bet_wins, actual_bet_losses
    global last_prediction, martingale_index, recent_outcomes
    
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
                latest_item = result_list[0]
                current_issue = latest_item.get("issueNumber")
                
                if current_issue != last_checked_issue:
                    current_num = int(latest_item.get("number"))
                    actual_outcome = "BIG" if current_num >= 5 else "SMALL"
                    
                    recent_outcomes.append(actual_outcome)
                    if len(recent_outcomes) > 15:
                        recent_outcomes.pop(0)

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
                            
                            status_text = "🔴 LOSE ❌ (" + str(consecutive_losses) + ")"
                    else:
                        status_text = "⚪ SKIPPED"

                    final_pred, pred_color, last_digit, logic_source = calculate_custom_prediction(current_issue, recent_outcomes)

                    total_actual_bets = actual_bet_wins + actual_bet_losses
                    win_rate = (actual_bet_wins / total_actual_bets * 100) if total_actual_bets > 0 else 100.0
                    
                    server_time = resp.get("serviceNowTime", "").split(' ')[-1]
                    
                    if final_pred == "WAIT":
                        display_pred = "🛑 WAIT (Period Digit: " + str(last_digit) + " | " + logic_source + ")"
                        last_prediction = "WAIT"
                        current_amount = BASE_BET
                    else:
                        display_pred = f"**{final_pred}** {pred_color} (Digit: {last_digit} | 🔍 {logic_source})"
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
