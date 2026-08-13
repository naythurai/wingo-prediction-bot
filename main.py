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
    return "AZBT LIVE TREND MONITOR ACTIVE", 200

# =====================================================================
# 2. CONFIGURATION & TOKENS (UPDATED TO LATEST DATA)
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"

TARGET_URL = "https://api.bigwinqaz.com/api/webapi/GetNoaverageEmerdList"

# 🔑 Updated Authorization Token from Request Headers
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg2NjY0NTU2IiwibmJmIjoiMTc4NjY2NDU1NiIsImV4cGlyYXRpb24iOiI4LzE0LzIwMjYgNjo0MjozNiBBTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjYwNTYzMiIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQ0FLWk4iLCJBbW91bnQiOiIzLjQwIiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI4LzE0LzIwMjYgNjoxMjozNiBBTSIsImxvZ2luSVBBZGRyZXNzIjoiODIuMjEuODQuMjA2IiwiRGJOdW1iZXIiOiIwIiwiSXN2YWxpZGF0b3IiOiIwIiwiS2V5Q29kZSI6IjE4MyIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjAiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiLCJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.lBJsGFt9fAWyNGeN_835KPh3hO8Kkqc7UrVhpdMF1ZI"

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

last_checked_issue = ""
recent_outcomes = []
last_logged_trend_state = False

# 📊 Prediction, Win & Max Lose Trackers
current_prediction = None
total_wins = 0
total_loses = 0
current_lose_streak = 0
max_lose_streak = 0

def send_msg(text):
    for cid in [CHAT_ID, GROUP_ID]:
        try: 
            bot.send_message(cid, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Send Error: {e}")

# ==========================================
# 3. PURE STABLE TREND ANALYZER & PREDICTOR
# ==========================================
def analyze_market_trend(outcome_history):
    if len(outcome_history) >= 6:
        last_few = outcome_history[-6:]
        
        # 1. Streak Trend (ဥပမာ: BIG သို့မဟုတ် SMALL ဆက်တိုက်)
        all_same = all(x == last_few[-1] for x in last_few[-3:])
        if all_same:
            next_pred = last_few[-1]  # Trend အတိုင်း လိုက်ခန့်မှန်းမည်
            return True, f"STREAK ({last_few[-1]})", next_pred

        # 2. Ping-Pong Trend (ဥပမာ: BIG, SMALL, BIG, SMALL တစ်လှည့်စီ)
        is_ping_pong = (last_few[-1] != last_few[-2]) and (last_few[-2] != last_few[-3]) and (last_few[-3] != last_few[-4])
        if is_ping_pong:
            next_pred = "SMALL" if last_few[-1] == "BIG" else "BIG"  # တစ်လှည့်စီ ပြောင်းခန့်မှန်းမည်
            return True, "PING-PONG (Alternating)", next_pred

    return False, "UNSTABLE", None

# ==========================================
# 4. FAST ENGINE CORE
# ==========================================
def check_and_process():
    global last_checked_issue, recent_outcomes, last_logged_trend_state
    global current_prediction, total_wins, total_loses, current_lose_streak, max_lose_streak
    
    # Updated payload params from latest API request
    payload = {
        "pageSize": 10,
        "pageNo": 1,
        "typeId": 30,
        "language": 7,
        "random": "2ab8f93cb0754e0eac87b3b3edf25558",
        "signature": "675E8126B88246F5D87DCE843D034636",
        "timestamp": int(time.time())
    }
    
    try:
        response = session.post(TARGET_URL, json=payload, timeout=5)
        resp = response.json()
        
        if response.status_code == 200 and resp.get("code") == 0 and resp.get("data"):
            result_list = resp["data"].get("list", [])
            if len(result_list) >= 6:
                latest_item = result_list[0]
                current_issue = latest_item.get("issueNumber")
                
                if current_issue != last_checked_issue:
                    current_num = int(latest_item.get("number"))
                    actual_outcome = "BIG" if current_num >= 5 else "SMALL"
                    
                    # 🏆 Win / Lose စစ်ဆေးခြင်း Logic
                    win_status_str = ""
                    if current_prediction is not None:
                        if actual_outcome == current_prediction:
                            total_wins += 1
                            current_lose_streak = 0
                            win_status_str = "🏆 **WIN!**"
                        else:
                            total_loses += 1
                            current_lose_streak += 1
                            # Max Lose တိုးသွားပါက Update လုပ်မည်
                            if current_lose_streak > max_lose_streak:
                                max_lose_streak = current_lose_streak
                            win_status_str = f"❌ **LOSE** (Lose Streak: {current_lose_streak})"

                    # 💡 0 နှင့် 5 ထွက်လာလျှင် အရင် ၅ ခု၏ Pattern ကို B/S ဖြင့် ဖမ်းယူခြင်း
                    pattern_text = ""
                    if current_num == 0 or current_num == 5:
                        prev_five = result_list[1:6]
                        p_list = []
                        for item in prev_five:
                            num = int(item.get("number"))
                            p_list.append("B" if num >= 5 else "S")
                        pattern_str = "".join(p_list)
                        pattern_text = f"\n🎯 **PATTERN (0 or 5):** `{pattern_str}`"

                    recent_outcomes.append(actual_outcome)
                    if len(recent_outcomes) > 15:
                        recent_outcomes.pop(0)

                    server_time = resp.get("serviceNowTime", "").split(' ')[-1]
                    
                    # Trend ငြိမ်မှု ရှိမရှိ စစ်ဆေးခြင်း
                    is_currently_stable, trend_detail, next_pred = analyze_market_trend(recent_outcomes)

                    # Trend စတင်ငြိမ်သွားသည့်အချိန် Telegram သို့ Message ပို့ခြင်း
                    if is_currently_stable and not last_logged_trend_state:
                        current_prediction = next_pred
                        msg = (f"🟢 **STABLE TREND DETECTED** 🟢\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"⏱️ **အချိန်:** `{server_time}`\n"
                               f"🎰 **Issue:** `{current_issue}`\n"
                               f"📊 **Trend ပုံစံ:** `{trend_detail}`\n"
                               f"🎲 **ရလဒ်:** `{current_num}` ({actual_outcome})\n"
                               f"🔮 **နောက်ပွဲခန့်မှန်းချက်:** `{next_pred}`\n"
                               f"{pattern_text}\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"🏆 **Wins:** `{total_wins}` | ❌ **Loses:** `{total_loses}`\n"
                               f"🔥 **Max Lose:** `{max_lose_streak}`\n"
                               f"━━━━━━━━━━━━━━━━━━━━")
                        send_msg(msg)
                        last_logged_trend_state = True
                    elif is_currently_stable and last_logged_trend_state:
                        # Trend ငြိမ်နေစဉ် ပွဲစဉ်တိုင်း၏ Win/Lose ရလဒ် ပို့ပေးခြင်း
                        msg = (f"🎰 **Issue:** `{current_issue}` | **ရလဒ်:** `{current_num}` ({actual_outcome})\n"
                               f"{win_status_str}\n"
                               f"🔮 **နောက်ပွဲခန့်မှန်းချက်:** `{next_pred}`\n"
                               f"{pattern_text}\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"🏆 **Wins:** `{total_wins}` | ❌ **Loses:** `{total_loses}` | 🔥 **Max Lose:** `{max_lose_streak}`")
                        send_msg(msg)
                        current_prediction = next_pred
                    elif not is_currently_stable:
                        last_logged_trend_state = False
                        current_prediction = None

                    last_checked_issue = current_issue

    except Exception as e:
        print(f"Error: {e}")

def realtime_loop():
    print("AZBT Live Trend Monitor Active...")
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
