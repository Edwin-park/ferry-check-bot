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

        lines = []

        for item in result_all:
            ships = item.get("ships", [])
            if not ships:
                continue  # ships 비어있으면 건너뜀

            ship = ships[0]
            vessel = ship.get("vessel", "선박명 없음")
            seat = ship.get("classes", "좌석 없음")
            departure = ship.get("departure", "출발지 없음")
            arrival = ship.get("arrival", "도착지 없음")
            duration = ship.get("requiredtime", "소요시간 없음")
            onlinecnt = int(ship.get("onlinecnt", 0))
            capacity = int(ship.get("capacity", 0))

            lines.append(
                f"- {vessel} / {seat}\n  {departure} → {arrival} ({duration})\n  잔여석: {onlinecnt}석 / 정원: {capacity}석"
            )

        if lines:
            message = f"🛳️ {date} 배편 현황 ({len(lines)}건)\n" + "\n\n".join(lines)
        else:
            message = f"❗ {date} 배편이 없습니다."

        send_telegram_message(BOT_TOKEN, CHAT_ID, message)

    except Exception as e:
        send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ [{date}] 오류 발생: {e}")

if __name__ == "__main__":
    check_ferry("2025-08-30")
