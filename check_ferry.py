import os
import requests
from collections import defaultdict

# 환경변수에서 토큰, 챗 ID 가져오기
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# 텔레그램 메시지 전송 함수
def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        res = requests.post(url, data=payload)
        print("✅ 텔레그램 응답:", res.text)
    except Exception as e:
        print("❗ 텔레그램 전송 오류:", e)

# 배편 조회 함수
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
        "t_portsubidlist": "1",    # 출발: 강릉
        "t_portidlist": "4311",
        "f_portsubidlist": "0",    # 도착: 울릉 저동
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

        # 같은 선박+시간을 묶어서 좌석 종류만 나누기
        grouped = defaultdict(list)
        for item in result_all:
            key = (
                item.get("vessel", "선박명 없음"),
                item.get("f_port", "출발지 없음"),
                item.get("departure", "시간 없음"),
                item.get("t_port", "도착지 없음"),
                item.get("arrival", "시간 없음"),
                item.get("requiredtime", "소요시간 없음")
            )
            grouped[key].append(item)

        lines = [f"🛳️ {date} 배편 현황"]
        for (vessel, f_port, dep_time, t_port, arr_time, duration), items in grouped.items():
            lines.append(f"- {vessel} ({f_port} {dep_time} → {t_port} {arr_time} / {duration})")
            for item in items:
                seat_name = item.get("classes", "좌석")
                online = int(item.get("onlinecnt", 0))
                total = int(item.get("capacity", 0))
                lines.append(f"  • {seat_name} (잔여 {online} / 정원 {total})")

        message = "\n".join(lines)
        send_telegram_message(BOT_TOKEN, CHAT_ID, message)

    except Exception as e:
        send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ [{date}] 오류 발생: {e}")

# ✅ 실행 부분
if __name__ == "__main__":
    check_ferry("2025-08-30")
