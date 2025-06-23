import os
import requests
from datetime import datetime

# ✅ 시간 제한: 오전 5시 ~ 밤 10시만 실행
now_hour = datetime.now().hour
if not (5 <= now_hour <= 22):
    print(f"⏸️ 현재 시간 {now_hour}시는 실행 시간대가 아닙니다.")
    exit()

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

def check_ferry(date: str):
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
        "t_portsubidlist": "1",
        "t_portidlist": "4311",
        "f_portsubidlist": "0",
        "f_portidlist": "4406",
        "lang": "ko",
        "sourcesiteid": "1PHSOBKSACLAIOD1XZMZ"
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result_all = response.json().get("data", {}).get("resultAll", [])

        if not result_all:
            send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ {date} 배편이 없습니다.")
            return

        lines = [f"🛳️ {date} 배편 현황"]
        grouped = {}

        for item in result_all:
            key = item.get("vessel", "") + item.get("departuretime", "")
            if key not in grouped:
                grouped[key] = {
                    "vessel": item.get("vessel", "선박명 없음"),
                    "departure": item.get("f_port", "출발지 없음"),
                    "departure_time": item.get("departure", "시간 없음"),
                    "arrival": item.get("t_port", "도착지 없음"),
                    "arrival_time": item.get("arrival", "시간 없음"),
                    "duration": item.get("requiredtime", "소요시간 없음"),
                    "seats": []
                }
            grouped[key]["seats"].append({
                "class": item.get("classes", "좌석"),
                "remain": int(item.get("onlinecnt", 0)),
                "total": int(item.get("capacity", 0))
            })

        for ferry in grouped.values():
            lines.append(f"- {ferry['vessel']} ({ferry['departure']} {ferry['departure_time']} → {ferry['arrival']} {ferry['arrival_time']} / {ferry['duration']})")
            for s in ferry["seats"]:
                lines.append(f"  • {s['class']}석 (잔여 {s['remain']} / 정원 {s['total']})")

        message = "\n".join(lines)
        send_telegram_message(BOT_TOKEN, CHAT_ID, message)

    except Exception as e:
        send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ [{date}] 오류 발생: {e}")

if __name__ == "__main__":
    check_ferry("2025-08-31")
