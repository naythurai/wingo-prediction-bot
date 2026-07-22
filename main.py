import os
import time
import requests
import telebot
from threading import Thread
from flask import Flask

# =====================================================================
# 1. FLASK APPLICATION (Render / Termux Background Keep-Alive)
# =====================================================================
app = Flask('')

@app.route('/')
def home():
    return "AZBT WINGO 1-MIN SAFE RECOVERY ENGINE ACTIVE", 200

# =====================================================================
# 2. CONFIGURATION & TOKENS
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"

# 🌟 API Endpoint
TARGET_URL = "https://api.bigwinqaz.com/api/webapi/GetEmerdList"

# 🌟 Header & Authorization Details
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0NjkwNjc3IiwibmJmIjoiMTc4NDY5MDY3NyIsImV4cGlyYXRpb24iOiI3LzIyLzIwMjYgMTA6MjQ6MzcgQU0iLCJyb2xlIjoiQWNjZXNzX1Rva2VuIiwidXNlcmlkIjo2MDU2MzIsInVzZXJuYW1lIjoiOTU5OTY2NTAyNjk1IiwidXNlcnBob3RvIjoiMSIsIm5pY2tuYW1lIjoiTWVtYmVyTk5HQ0FLWk4iLCJhbW91bnQiOiI2LjAwIiwiaW50ZWdyYWwiOiIwIiwibG9naW5tYXJrIjoiSDUiLCJsb2dpbnRpbWUiOiI3LzIyLzIwMjYgOTo1NDozNyBBTSIsImxvZ2luaXBhZGRyZXNzIjoiODIuMjEuODQuODIiLCJkYm51bWJlciI6IjAiLCJpc3ZhbGlkYXRvciI6IjAiLCJrZXljb2RlIjoiMTA0IiwidG9rZW50eXBlIjoiQWNjZXNzX1Rva2VuIiwicGhvbmV0eXBlIjoiMSIsInVzZXJ0eXBlIjoiMCIsInVzZXJOYW1lMiI6IiIsImlzcyI6Imp3dElzc3VlciIsImF1ZCI6ImxvdHRlcnlUaWNrZXQifQ.pjZp8XV4YcZxWFPNhkaJ0z3p8qJx3bjIja1id7QAaow"

bot = telebot.TeleBot(TOKEN)

BASE_BET = 100
MARTINGALE_STEPS = [1, 3, 8, 24, 72, 216, 648, 1944, 5832]
martingale_index = 0

last_winning_num = -1
actual_current_losses = 0  # အမှန်တကယ် ထိုးပြီး လက်ရှိ ဆက်တိုက် ရှုံးနေသည့် အကြိမ်
actual_max_losses = 0      # အမှန်တကယ် ထိုးပြီး အများဆုံး ဆက်တိုက် ရှုံးခဲ့သည့် အကြိမ်
actual_bet_wins = 0        # အမှန်တကယ် ထိုးပြီး နိုင်သည့် အကြိမ်
actual_bet_losses = 0      # အမှန်တကယ် ထိုးပြီး ရှုံးသည့် စုစုပေါင်း အကြိမ်
last_prediction = ""

# 🛡️ 1-Loss Pause & Auto-Recovery State Variables
is_paused = False
shadow_prediction = ""

def send_msg(text):
    for cid in [CHAT_ID, GROUP_ID]:
        try: 
            bot.send_message(cid, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Telegram Send Error: {e}")

# ==========================================
# 🧠 Big/Small Count Calculation Logic
# ==========================================
def calculate_prediction_from_grid(data_list):
    try:
        freq_data = next((item for item in data_list if item.get("type") == 1), None)
        if not freq_data:
            return "WAIT"
            
        small_total = sum(freq_data.get(f"number_{i}", 0) for i in range(5))
        big_total = sum(freq_data.get(f"number_{i}", 0) for i in range(5, 10))
        
        # 🌟 အရေအတွက် တူနေပါက WAIT ဟု ပြန်ပေးမည်
        if big_total == small_total:
            return "WAIT"
        
        return "BIG" if big_total > small_total else "SMALL"
    except Exception as e:
        return "WAIT"

# ==========================================
# 3. PURE REALTIME ENGINE (GetEmerdList API)
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
                # Missing count = 0 ဖြစ်နေသည့် ဂဏန်းသည် လက်ရှိထွက်ထားသော ဂဏန်းဖြစ်သည်
                current_num = -1
                for i in range(10):
                    if missing_data.get(f"number_{i}") == 0:
                        current_num = i
                        break
                
                # အဖြေအသစ် ထွက်လာမှသာ စိစစ်မည်
                if current_num != -1 and current_num != last_winning_num:
                    actual_outcome = "BIG" if current_num >= 5 else "SMALL"
                    is_win_event = False
                    
                    # -------------------------------------------------------------
                    # ၁။ ပြီးခဲ့သော အလှည့် ရလဒ် စိစစ်ခြင်း & 1-LOSS PAUSE LOGIC
                    # -------------------------------------------------------------
                    if is_paused:
                        # WAIT Mode ရောက်နေချိန်: နောက်ကွယ်မှ Shadow Signal ကို တိုက်စစ်သည်
                        if shadow_prediction and shadow_prediction != "WAIT" and shadow_prediction == actual_outcome:
                            is_paused = False
                            actual_current_losses = 0
                            martingale_index = 0
                            status_text = "🟢 RECOVERED (Signal ပြန်ဖွင့်ပါပြီ)"
                            is_win_event = True
                        else:
                            status_text = "🟡 PAUSED (စောင့်ကြည့်ဆဲ...)"
                    else:
                        # NORMAL Mode ရောက်နေချိန် (အမှန်တကယ် ထိုးသည့် အကြိမ်များ)
                        if last_prediction and last_prediction != "WAIT":
                            if last_prediction == actual_outcome:
                                actual_bet_wins += 1
                                actual_current_losses = 0
                                martingale_index = 0  
                                status_text = "🟢 WIN ✅ (အနိုင်ရရှိပါသည်)"
                                is_win_event = True
                            else:
                                actual_bet_losses += 1
                                actual_current_losses += 1
                                
                                if actual_current_losses > actual_max_losses:
                                    actual_max_losses = actual_current_losses
                                
                                # ၁ ကြိမ် ရှုံးသည်နှင့် PAUSE Mode ချက်ချင်းဝင်မည်
                                is_paused = True
                                status_text = "🔴 LOSE (၁ ကြိမ်မှားသဖြင့် WAIT ခိုင်းထားပါသည်)"
                        else:
                            status_text = "⚪ SKIPPED / WAITING"

                    # -------------------------------------------------------------
                    # ၂။ နောက်တစ်ကြိမ်အတွက် PREDICTION & WINRATE တွက်ယူခြင်း
                    # -------------------------------------------------------------
                    raw_pred = calculate_prediction_from_grid(data_list)
                    
                    # အမှန်တကယ် ထိုးထားသည့် အကြိမ်များပေါ်တွင်သာ Win Rate တွက်ချက်ခြင်း
                    total_actual_bets = actual_bet_wins + actual_bet_losses
                    win_rate = (actual_bet_wins / total_actual_bets * 100) if total_actual_bets > 0 else 100.0
                    
                    server_time = resp.get("serviceNowTime", "").split(' ')[-1]
                    
                    if is_paused:
                        display_pred = "🛑 WAIT (စောင့်ကြည့်ပါ)"
                        shadow_prediction = raw_pred  # နောက်ကွယ်တွင် ခန့်မှန်းချက် မှတ်ထားမည်
                        last_prediction = "WAIT"
                        current_amount = BASE_BET
                    elif raw_pred == "WAIT":
                        display_pred = "🛑 WAIT (Big/Small အရေအတွက် တူနေပါသည်)"
                        shadow_prediction = ""
                        last_prediction = "WAIT"
                        current_amount = BASE_BET
                    else:
                        display_pred = f"**{raw_pred}**"
                        shadow_prediction = ""
                        last_prediction = raw_pred
                        current_amount = BASE_BET * MARTINGALE_STEPS[martingale_index]

                    # -------------------------------------------------------------
                    # ၃။ TELEGRAM MESSAGE ပို့ဆောင်ခြင်း (WIN ရင် 🏆🏆🏆 ပြမည်)
                    # -------------------------------------------------------------
                    if is_win_event:
                        header_banner = "====================================\n🏆🏆🏆 CONGRATULATIONS! WIN! 🏆🏆🏆\n===================================="
                    else:
                        header_banner = "🔮 **AZBT REAL-SYNC WINGO PREDICTION** 🔮"

                    msg = (f"{header_banner}\n"
                           f"━━━━━━━━━━━━━━━━━━\n"
                           f"🎯 **Bet (ခန့်မှန်းချက်):** {display_pred}\n"
                           f"━━━━━━━━━━━━━━━━━━\n"
                           f"🎰 **Last Result:** Number `{current_num}` ({actual_outcome})\n"
                           f"📊 **Win/Lose Status:** {status_text}\n"
                           f"💵 **BET AMOUNT:** `{current_amount:,} MMK` (Step {martingale_index + 1})\n"
                           f"📈 **ACTUAL WINRATE:** `{win_rate:.1f}%` (W: {actual_bet_wins} / L: {actual_bet_losses})\n"
                           f"📉 **LOSS TRACKER:** Max Lose `{actual_max_losses}` ကြိမ် | Current Lose `{actual_current_losses}` ကြိမ်\n"
                           f"⏱️ **Server Time:** `{server_time}`\n"
                           f"━━━━━━━━━━━━━━━━━━")
                    
                    send_msg(msg)
                    last_winning_num = current_num

    except Exception as e:
        print(f"Connection Waiting: {e}")

def realtime_loop():
    print("AZBT Real-Sync Engine Active with WIN Trophy Banner...")
    while True:
        check_and_process()
        time.sleep(2)

# =====================================================================
# 4. RUN ENGINE
# =====================================================================
Thread(target=realtime_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
