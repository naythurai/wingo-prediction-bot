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
    return "AZBT WINGO 1-MIN PURE REALTIME ENGINE IS ACTIVE", 200

# =====================================================================
# 2. CONFIGURATION & TOKENS (Token လုံးဝမလိုသော ကမ္ဘာသုံး Public API စနစ်)
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"

# 🌟 Token မလိုဘဲ Realtime ဒေတာ တိုက်ရိုက်ဆွဲနိုင်သော စနစ်သို့ ပြောင်းလဲခြင်း
TARGET_URL = "https://api.cklottery.online/api/webapi/GetNoaverageEmerdList"

PAYLOAD_DATA = {
    "pageSize": 10,
    "pageNo": 1,
    "typeId": 1,
    "language": 0
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
        except Exception as e:
            print(f"Telegram Error: {e}")

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
        return "BIG"

# ==========================================
# 3. PURE REALTIME ENGINE (100% ဒေတာအစစ်)
# ==========================================
def check_and_process():
    global last_issue, losses_count, max_losses, total_wins, total_losses, last_prediction, martingale_index
    
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # Token မပါဘဲ လှမ်းတောင်းခြင်း
        response = requests.post(TARGET_URL, json=PAYLOAD_DATA, headers=headers, timeout=6)
        resp = response.json()
        
        if response.status_code == 200 and resp.get("code") == 0 and resp.get("data", {}).get("list"):
            latest = resp["data"]["list"][0]
            issue = str(latest["issueNumber"])
            num = int(latest["number"])
            
            # ဂိမ်းထဲမှာ အလှည့်အသစ် တကယ်ပြောင်းမှသာ စာပို့မည်
            if issue != last_issue:
                actual_outcome = "BIG" if num >= 5 else "SMALL"
                
                if last_prediction:
                    if last_prediction == actual_outcome:
                        total_wins += 1; losses_count = 0; martingale_index = 0  
                    else:
                        total_losses += 1; losses_count += 1
                        if losses_count > max_losses: max_losses = losses_count
                        if martingale_index < len(MARTINGALE_STEPS) - 1: martingale_index += 1
                        else: martingale_index = 0 

                pred = calculate_prediction(issue, num)
                current_amount = BASE_BET * MARTINGALE_STEPS[martingale_index]
                next_issue = str(int(issue) + 1)
                win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 100
                
                # 🌟 Live Connection Lost စာတန်းကြီးကို ထာဝရ ဖြုတ်ချလိုက်ပါပြီ
                msg = (f"🔮 **WINGO 1-MIN PREDICTION** 🔮\n"
                       f"━━━━━━━━━━━━━━━━━━\n"
                       f"🆔 **Next Period:** `{next_issue}`\n"
                       f"🎯 **Bet (ခန့်မှန်းချက်):** **{pred}**\n"
                       f"━━━━━━━━━━━━━━━━━━\n"
                       f"🎰 **Last Result:** `{issue}` -> `{num}` ({actual_outcome})\n"
                       f"📊 **Win/Lose:** " + ("🟢 WIN" if losses_count == 0 and total_wins > 0 else "🔴 LOSE" if losses_count > 0 else "Waiting... ⏳") + f"\n"
                       f"💵 **BET AMOUNT:** `{current_amount:,} MMK` (Step {martingale_index + 1})\n"
                       f"📈 **WINRATE:** `{win_rate:.1f}%`\n"
                       f"📉 **MAX LOSE:** `{max_losses} ကြိမ်` (Current Lose: `{losses_count}`)\n"
                       f"━━━━━━━━━━━━━━━━━━")
                
                send_msg(msg)
                last_issue, last_prediction = issue, pred
    except Exception as e:
        print(f"Connection Waiting: {e}")

def realtime_loop():
    print("AZBT Public Core Realtime Engine Running...")
    while True:
        check_and_process()
        time.sleep(1.5) # ၁.၅ စက္ကန့်တစ်ခါ ဆာဗာကို Realtime ထိုင်စောင့်ကြည့်မည်

# =====================================================================
# 4. RUN ENGINE
# =====================================================================
Thread(target=realtime_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
