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

# 🌟 ပေးပို့ထားသော API Endpoint အသစ်
TARGET_URL = "https://api.bigwinqaz.com/api/webapi/GetEmerdList"

# 🌟 Header & Authorization Details
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg0NjkwNjc3IiwibmJmIjoiMTc4NDY5MDY3NyIsImV4cGlyYXRpb24iOiI3LzIyLzIwMjYgMTA6MjQ6MzcgQU0iLCJyb2xlIjoiQWNjZXNzX1Rva2VuIiwidXNlcmlkIjo2MDU2MzIsInVzZXJuYW1lIjoiOTU5OTY2NTAyNjk1IiwidXNlcnBob3RvIjoiMSIsIm5pY2tuYW1lIjoiTWVtYmVyTk5HQ0FLWk4iLCJhbW91bnQiOiI2LjAwIiwiaW50ZWdyYWwiOiIwIiwibG9naW5tYXJrIjoiSDUiLCJsb2dpbnRpbWUiOiI3LzIyLzIwMjYgOTo1NDozNyBBTSIsImxvZ2luaXBhZGRyZXNzIjoiODIuMjEuODQuODIiLCJkYm51bWJlciI6IjAiLCJpc3ZhbGlkYXRvciI6IjAiLCJrZXljb2RlIjoiMTA0IiwidG9rZW50eXBlIjoiQWNjZXNzX1Rva2VuIiwicGhvbmV0eXBlIjoiMSIsInVzZXJ0eXBlIjoiMCIsInVzZXJuYW1lMiI6IiIsImlzcyI6Imp3dElzc3VlciIsImF1ZCI6ImxvdHRlcnlUaWNrZXQifQ.pjZp8XV4YcZxWFPNhkaJ0z3p8qJx3bjIja1id7QAaow"

bot = telebot.TeleBot(TOKEN)

BASE_BET = 100
MARTINGALE_STEPS = [1, 3, 8, 24, 72, 216, 648, 1944, 5832]
martingale_index = 0

last_winning_num = -1
losses_count = 0
max_losses = 0
total_wins = 0
total_losses = 0
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
# 🧠 Frequency & Trend Calculation Logic
# ==========================================
def calculate_prediction_from_grid(data_list):
    try:
        freq_data = next((item for item in data_list if item.get("type") == 1), None)
        if not freq_data:
            return "BIG"
            
        small_total = sum(freq_data.get(f"number_{i}", 0) for i in range(5))
        big_total = sum(freq_data.get(f"number_{i}", 0) for i in range(5, 10))
        
        return "BIG" if big_total >= small_total else "SMALL"
    except Exception as e:
        return "BIG"

# ==========================================
# 3. PURE REALTIME ENGINE (GetEmerdList API)
# ==========================================
def check_and_process():
    global last_winning_num, losses_count, max_losses, total_wins, total_losses
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
                    
                    # -------------------------------------------------------------
                    # ၁။ ပြီးခဲ့သော အလှည့် ရလဒ် စိစစ်ခြင်း & 1-LOSS PAUSE LOGIC
                    # -------------------------------------------------------------
                    if is_paused:
                        # WAIT Mode ရောက်နေချိန်: နောက်ကွယ်မှ Shadow Signal ကို တိုက်စစ်သည်
                        if shadow_prediction and shadow_prediction == actual_outcome:
                            is_paused = False
                            losses_count = 0
                            martingale_index = 0
                            status_text = "🟢 RECOVERED (Signal ပြန်ဖွင့်ပါပြီ)"
                        else:
                            status_text = "🟡 PAUSED (စောင့်ကြည့်ဆဲ...)"
                    else:
                        # NORMAL Mode ရောက်နေချိန်
                        if last_prediction and last_prediction != "WAIT":
                            if last_prediction == actual_outcome:
                                total_wins += 1
                                losses_count = 0
                                martingale_index = 0  
                                status_text = "🟢 WIN"
                            else:
                                total_losses += 1
                                losses_count += 1
                                if losses_count > max_losses:
                                    max_losses = losses_count
                                
                                # ၁ ကြိမ် ရှုံးသည်နှင့် PAUSE Mode ချက်ချင်းဝင်မည်
                                is_paused = True
                                status_text = "🔴 LOSE (၁ ကြိမ်မှားသဖြင့် WAIT ခိုင်းထားပါသည်)"

                    # -------------------------------------------------------------
                    # ၂။ နောက်တစ်ကြိမ်အတွက် PREDICTION ထုတ်ယူခြင်း
                    # -------------------------------------------------------------
                    raw_pred = calculate_prediction_from_grid(data_list)
                    win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 100
                    server_time = resp.get("serviceNowTime", "")
                    
                    if is_paused:
                        display_pred = "🛑 WAIT (စောင့်ကြည့်ပါ)"
                        shadow_prediction = raw_pred  # နောက်ကွယ်တွင် ခန့်မှန်းချက် မှတ်ထားမည်
                        last_prediction = "WAIT"
                        current_amount = BASE_BET
                    else:
                        display_pred = f"**{raw_pred}**"
                        shadow_prediction = ""
                        last_prediction = raw_pred
                        current_amount = BASE_BET * MARTINGALE_STEPS[martingale_index]

                    # -------------------------------------------------------------
                    # ၃။ TELEGRAM MESSAGE ပို့ဆောင်ခြင်း
                    # -------------------------------------------------------------
                    msg = (f"🔮 **AZBT REAL-SYNC WINGO PREDICTION** 🔮\n"
                           f"━━━━━━━━━━━━━━━━━━\n"
                           f"🎯 **Bet (ခန့်မှန်းချက်):** {display_pred}\n"
                           f"━━━━━━━━━━━━━━━━━━\n"
                           f"🎰 **Last Result:** Number `{current_num}` ({actual_outcome})\n"
                           f"📊 **Win/Lose Status:** {status_text}\n"
                           f"💵 **BET AMOUNT:** `{current_amount:,} MMK` (Step {martingale_index + 1})\n"
                           f"📈 **WINRATE:** `{win_rate:.1f}%`\n"
                           f"📉 **MAX LOSE:** `{max_losses} ကြိမ်` (Current Lose: `{losses_count}`)\n"
                           f"⏱️ **Server Time:** `{server_time}`\n"
                           f"━━━━━━━━━━━━━━━━━━")
                    
                    send_msg(msg)
                    last_winning_num = current_num

    except Exception as e:
        print(f"Connection Waiting: {e}")

def realtime_loop():
    print("AZBT Real-Sync Engine Active with GetEmerdList API...")
    while True:
        check_and_process()
        time.sleep(2) # 2 စက္ကန့်တစ်ခါ ဆာဗာကို တိုက်ရိုက် Sync လုပ်မည်

# =====================================================================
# 4. RUN ENGINE
# =====================================================================
Thread(target=realtime_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
