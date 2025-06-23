import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=payload)
        print("텔레그램 응답:", response.text)
    except Exception as e:
        print("텔레그램 전송 오류:", e)

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
        res_json = response.json()
        result_all = res_json.get("data", {}).get("resultAll", [])

        if not result_all:
            send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ {date} 배편이 없습니다.")
        else:
            lines = [f"🛳️ {date} 배편 현황 ({len(result_all)}건)"]
            for item in result_all:
                vessel = item.get("vessel", "선박명 없음")
                seat = item.get("classes", "좌석 구분 없음")
                departure = item.get("departure", "출발지 미표시")
                arrival = item.get("arrival", "도착지 미표시")
                duration = item.get("requiredtime", "소요시간 없음")
                onlinecnt = int(item.get("onlinecnt", 0))
                capacity = int(item.get("capacity", 0))

                lines.append(
                    f"- {vessel} / {seat} / {departure} → {arrival} ({duration})\n  잔여석: {onlinecnt}석 / 정원: {capacity}석"
                )

            message = "\n".join(lines)
            send_telegram_message(BOT_TOKEN, CHAT_ID, message)

    except Exception as e:
        print("오류 발생:", e)
        send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ 오류 발생: {e}")

if __name__ == "__main__":
    check_ferry("2025-08-30")
