import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        res = requests.post(url, data=payload)
        print("✅ 텔레그램 응답:", res.text)
    except Exception as e:
        print("❗ 텔레그램 전송 오류:", e)

def fetch_and_send(date: str):
    url = "https://island.theksa.co.kr/booking/selectDepartureList"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://island.theksa.co.kr",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://island.theksa.co.kr/",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {
        "masterdate": date,
        "t_portsubidlist": "1",  # 출발: 강릉
        "t_portidlist": "4311",
        "f_portsubidlist": "0",  # 도착: 울릉 저동
        "f_portidlist": "4406",
        "lang": "ko",
        "sourcesiteid": "1PHSOBKSACLAIOD1XZMZ"
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        results = response.json().get("data", {}).get("resultAll", [])

        if not results:
            send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ {date} 배편이 없습니다.")
            return

        lines = [f"🛳️ {date} 배편 현황"]
        grouped = {}

        for r in results:
            key = (r["vessel"], r["departure"], r["arrival"], r["requiredtime"])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append((r["classes"], int(r["onlinecnt"]), int(r["capacity"])))

        for (vessel, dep, arr, duration), seats in grouped.items():
            lines.append(f"- {vessel} (강릉 {dep} → 울릉_저동 {arr} / {duration})")
            for seat_name, online, total in seats:
                lines.append(f"  • {seat_name}석 (잔여 {online} / 정원 {total})")

        send_telegram_message(BOT_TOKEN, CHAT_ID, "\n".join(lines))

    except Exception as e:
        send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ [{date}] 오류 발생: {e}")

# ✅ 여러 날짜 확인
if __name__ == "__main__":
    for date in ["2025-08-30", "2025-09-13"]:
        fetch_and_send(date)
