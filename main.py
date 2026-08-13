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
# 2. CONFIGURATION & TOKENS
# =====================================================================
TOKEN = "8877327172:AAEJ5BHMEHRm82a4gBBRkaRmkSmn_IFl7LY"
CHAT_ID = "5491984866"
GROUP_ID = "-1003803779601"

TARGET_URL = "https://api.bigwinqaz.com/api/webapi/GetNoaverageEmerdList"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzg1MzA5MzAyIiwibmJmIjoiMTc4FSB0MjkzMDIiLCJleHAiOiIxNzg1MzExMDIiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiI3LzI5LzIwMjYgMjoxNTowMiBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsImVzZXJJZCI6IjYwNTYzMiIsIlVzZXJOYW1lIjoiOTU5OTY2NTAyNjk1IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYmVyTk5HQ0FLWk4iLCJBbW91bnQiOiI0LjAwIiwiSW50ZWdyYWwiOiIwIiwiTG9naW5NYXJrIjoiSDUiLCJMb2dpblRpbWUiOiI3LzI5LzIwMjYgMTo0NTowMiBQTSIsImxvZ2luSVBBZGRyZXNzIjoiNDUuMTk2LjE2LjIzNyIsImRiTnVtYmVyIjoiMCIsIklzdmFsaWRhdG9yIjoiMCIsIktleUNvZGUiOiIxMzciLCJUb2tlblR5cGUiOiJBY2Nlc3NfVG9rZW4iLCJQaG9uZVR5cGUiOiIxIiwiVXNlciJUeXBlIjoiMCIsIlVzZXJOYW1lMiI6IiIsImlzcyI6nd0SXNzdWVyIiwiYXVkIjoibG90dGVyeVRpY2tldCJ9.zJh3XG2q9a40dCQ3z1tm8oUvvh1iVgeNE93RyIAP6CQ"

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

def send_msg(text):
    for cid in [CHAT_ID, GROUP_ID]:
        try: 
            bot.send_message(cid, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Send Error: {e}")

# ==========================================
# 3. PURE STABLE TREND ANALYZER
# ==========================================
def analyze_market_trend(outcome_history):
    if len(outcome_history) >= 6:
        last_few = outcome_history[-6:]
        
        # 1. Streak Trend (နောက်ဆုံး ၃ ခု တူနေခြင်း - ဥပမာ BIG သို့မဟုတ် SMALL ဆက်တိုက်)
        all_same = all(x == last_few[-1] for x in last_few[-3:])
        if all_same:
            return True, f"STREAK ({last_few[-1]})"

        # 2. Ping-Pong Trend (တစ်လှည့်စီ ထွက်နေခြင်း - ဥပမာ BIG, SMALL, BIG, SMALL)
        is_ping_pong = (last_few[-1] != last_few[-2]) and (last_few[-2] != last_few[-3]) and (last_few[-3] != last_few[-4])
        if is_ping_pong:
            return True, "PING-PONG (Alternating)"

    return False, "UNSTABLE"

# ==========================================
# 4. FAST ENGINE CORE
# ==========================================
def check_and_process():
    global last_checked_issue, recent_outcomes, last_logged_trend_state
    
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
            if len(result_list) >= 6: # လုံလောက်သော အချက်အလက်ရှိရန် အနည်းဆုံး ၆ ခု လိုအပ်သည် (ယခုထွက် + အရင် ၅ ခု)
                latest_item = result_list[0]
                current_issue = latest_item.get("issueNumber")
                
                if current_issue != last_checked_issue:
                    current_num = int(latest_item.get("number"))
                    actual_outcome = "BIG" if current_num >= 5 else "SMALL"
                    
                    # 💡 0 နှင့် 5 ထွက်လာခြင်း ရှိမရှိ စစ်ဆေးပြီး အရင် ၅ ခုရဲ့ Pattern ကို ယူခြင်း
                    special_pattern_msg = ""
                    if current_num == 0 or current_num == 5:
                        # result_list[1] မှစတင်ပြီး အရင် ၅ ခုကို ယူမည် (index 1 to 5)
                        previous_five_items = result_list[1:6]
                        pattern_list = []
                        for item in previous_five_items:
                            num = int(item.get("number"))
                            # B = BIG, S = SMALL အနေဖြင့် အတိုကောက်ယူရန် (သို့မဟုတ် စာသားအပြည့်လည်း သုံးနိုင်သည်)
                            p_out = "B" if num >= 5 else "S"
                            pattern_list.append(p_out)
                        
                        # စာသားပုံစံ ဖန်တီးခြင်း (ဥပမာ: S, S, B, B, S သို့မဟုတ် SS BBS)
                        pattern_str = "".join(pattern_list)
                        special_pattern_msg = (f"\n🎯 **SPECIAL ZERO/FIVE ALERT!** 🎯\n"
                                               f"🔢 နံပါတ် **{current_num}** ကျလာပါသည်!\n"
                                               f"📋 **အရင် ၅ ခု Pattern:** `{pattern_str}`\n")

                    recent_outcomes.append(actual_outcome)
                    if len(recent_outcomes) > 15:
                        recent_outcomes.pop(0)

                    server_time = resp.get("serviceNowTime", "").split(' ')[-1]
                    
                    # Trend ငြိမ်မှု ရှိမရှိ စစ်ဆေးခြင်း
                    is_currently_stable, trend_detail = analyze_market_trend(recent_outcomes)

                    # Trend အသစ် စတင်တည်ငြိမ်သွားသည့် အချိန်ကို မှတ်သားပြီး Telegram သို့ ပို့မည်
                    if is_currently_stable and not last_logged_trend_state:
                        msg = (f"🟢 **STABLE TREND DETECTED** 🟢\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"⏱️ **အချိန်:** `{server_time}`\n"
                               f"🎰 **Issue:** `{current_issue}`\n"
                               f"📊 **Trend ပုံစံ:** `{trend_detail}`\n"
                               f"🎲 **နောက်ဆုံးထွက်ရလဒ်:** `{current_num}` ({actual_outcome})\n"
                               f"{special_pattern_msg}"
                               f"━━━━━━━━━━━━━━━━━━━━")
                        send_msg(msg)
                        last_logged_trend_state = True
                    elif not is_currently_stable:
                        last_logged_trend_state = False
                        # အကယ်၍ Trend မငြိမ်ဘဲ 0 သို့မဟုတ် 5 သက်သက် ထွက်လာရင်တောင် Alert ပို့ချင်ရင် ဒီအောက်မှာ ထည့်လို့ရပါတယ်။

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
