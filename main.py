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
    return "AZBT REAL ENGINE ACTIVE", 200

# =====================================================================
# 2. CONFIGURATION & TOKENS
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"

TARGET_URL = "https://api.bigwinqaz.com/api/webapi/GetEmerdList"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0NjkwNjc3IiwibmJmIjoiMTc4NDY5MDY3NyIsImV4cGlyYXRpb24iOiI3LzIyLzIwMjYgMTA6MjQ6MzcgQU0iLCJyb2xlIjoiQWNjZXNzX1Rva2VuIiwidXNlcmlkIjo2MDU2MzIsInVzZXJuYW1lIjoiOTU5OTY2NTAyNjk1IiwidXNlcnBob3RvIjoiMSIsIm5pY2tuYW1lIjoiTWVtYmVyTk5HQ0FLWk4iLCJhbW91bnQiOiI2LjAwIiwiaW50ZWdyYWwiOiIwIiwibG9naW5tYXJrIjoiSDUiLCJsb2dpbnRpbWUiOiI3LzIyLzIwMjYgOTo1NDozNyBBTSIsImxvZ2luaXBhZGRyZXNzIjoiODIuMjEuODQuODIiLCJkYm51bWJlciI6IjAiLCJpc3ZhbGlkYXRvciI6IjAiLCJrZXljb2RlIjoiMTA0IiwidG9rZW50eXBlIjoiQWNjZXNzX1Rva2VuIiwicGhvbmV0eXBlIjoiMSIsInVzZXJ0eXBlIjoiMCIsInVzZXJOYW1lMiI6IiIsImlzcyI6Imp3dElzc3VlciIsImF1ZCI6ImxvdHRlcnlUaWNrZXQifQ.pjZp8XV4YcZxWFPNhkaJ0z3p8qJx3bjIja1id7QAaow"

bot = telebot.TeleBot(TOKEN)

BASE_BET = 100
MARTINGALE_STEPS = [1, 3, 8, 24, 72, 216, 648, 1944, 5832]
martingale_index = 0

last_winning_num = -1
actual_current_losses = 0
actual_max_losses = 0
actual_bet_wins = 0
actual_bet_losses = 0
last_prediction = ""

is_paused = False
shadow_prediction = ""

def send_msg(text):
    for cid in [CHAT_ID, GROUP_ID]:
        try: 
            bot.send_message(cid, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Send Error: {e}")

# ==========================================
# 3. PREDICTION LOGIC
# ==========================================
def calculate_prediction_from_grid(data_list):
    try:
        freq_data = next((item for item in data_list if item.get("type") == 1), None)
        if not freq_data:
            return "WAIT"
            
        small_total = sum(freq_data.get(f"number_{i}", 0) for i in range(5))
        big_total = sum(freq_data.get(f"number_{i}", 0) for i in range(5, 10))
        
        if big_total == small_total:
            return "WAIT"
        
        return "BIG" if big_total > small_total else "SMALL"
    except Exception as e:
        return "WAIT"

# ==========================================
# 4. ENGINE CORE
# ==========================================
def check_and_process():
    global last_winning_num, actual_current_losses, actual_max_losses
    global actual_bet_wins, actual_bet_losses
    global last_prediction, martingale_index, is_paused, shadow_prediction
    
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Authorization": AUTH_TOKEN,
        "Ar-Origin": "https://www.bigwingame.cc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "typeId": 30,
        "language": 7,
        "random": "eb86d837aa1c4edd956e11b69bce20c4",
        "signature": "DB0AE80547464D7EA5C377F7B4BECB74",
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(TARGET_URL, json=payload, headers=headers, timeout=6)
        resp = response.json()
        
        if response.status_code == 200 and resp.get("code") == 0 and resp.get("data"):
            data_list = resp["data"]
            missing_data = next((item for item in data_list if item.get("type") == 2), None)
            
            if missing_data:
                current_num = -1
                for i in range(10):
                    if missing_data.get(f"number_{i}") == 0:
                        current_num = i
                        break
                
                if current_num != -1 and current_num != last_winning_num:
                    actual_outcome = "BIG" if current_num >= 5 else "SMALL"
                    is_win_event = False
                    
                    if is_paused:
                        if shadow_prediction and shadow_prediction != "WAIT" and shadow_prediction == actual_outcome:
                            is_paused = False
                            actual_current_losses = 0
                            martingale_index = 0
                            status_text = "🟢 RECOVERED"
                            is_win_event = True
                        else:
                            status_text = "🟡 PAUSED"
                    else:
                        if last_prediction and last_prediction != "WAIT":
                            if last_prediction == actual_outcome:
                                actual_bet_wins += 1
                                actual_current_losses = 0
                                martingale_index = 0
                                status_text = "🟢 WIN ✅"
                                is_win_event = True
                            else:
                                actual_bet_losses += 1
                                actual_current_losses += 1
                                
                                if martingale_index < len(MARTINGALE_STEPS) - 1:
                                    martingale_index += 1
                                
                                if actual_current_losses > actual_max_losses:
                                    actual_max_losses = actual_current_losses
                                
                                is_paused = True
                                status_text = "🔴 LOSE ❌"
                        else:
                            status_text = "⚪ SKIPPED"

                    raw_pred = calculate_prediction_from_grid(data_list)
                    
                    total_actual_bets = actual_bet_wins + actual_bet_losses
                    win_rate = (actual_bet_wins / total_actual_bets * 100) if total_actual_bets > 0 else 100.0
                    
                    server_time = resp.get("serviceNowTime", "").split(' ')[-1]
                    
                    if is_paused:
                        display_pred = "🛑 WAIT"
                        shadow_prediction = raw_pred
                        last_prediction = "WAIT"
                        current_amount = BASE_BET
                    elif raw_pred == "WAIT":
                        display_pred = "🛑 WAIT"
                        shadow_prediction = ""
                        last_prediction = "WAIT"
                        current_amount = BASE_BET
                    else:
                        display_pred = f"**{raw_pred}**"
                        shadow_prediction = ""
                        last_prediction = raw_pred
                        current_amount = BASE_BET * MARTINGALE_STEPS[martingale_index]

                    if is_win_event:
                        header_banner = "🏆🏆🏆 **WIN RESULT** 🏆🏆🏆"
                    else:
                        header_banner = "⚡ **AZBT REAL-SYNC ENGINE** ⚡"

                    msg = (f"{header_banner}\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n"
                           f"🎯 **SIGNAL:** {display_pred}\n"
                           f"🎰 **RESULT:** `{current_num}` ({actual_outcome})\n"
                           f"📊 **STATUS:** {status_text}\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n"
                           f"💵 **BET:** `{current_amount:,} MMK` (Step {martingale_index + 1})\n"
                           f"📈 **WIN RATE:** `{win_rate:.1f}%` (W: `{actual_bet_wins}` | L: `{actual_bet_losses}`)\n"
                           f"📉 **LOSS:** Max `{actual_max_losses}` | Current `{actual_current_losses}`\n"
                           f"⏱️ **TIME:** `{server_time}`\n"
                           f"━━━━━━━━━━━━━━━━━━━━")
                    
                    send_msg(msg)
                    last_winning_num = current_num

    except Exception as e:
        print(f"Waiting: {e}")

def realtime_loop():
    print("AZBT Clean Engine Active...")
    while True:
        check_and_process()
        time.sleep(2)

# =====================================================================
# 5. RUN
# =====================================================================
Thread(target=realtime_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
