import os
import requests
from datetime import datetime

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

# 날짜별 배편 조회 함수
def get_ferry_info(date: str) -> str:
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
            return f"🛳️ {date} 배편 없음"

        grouped = {}
        for item in result_all:
            vessel = item.get("vessel", "선박명 없음")
            departure = item.get("departure", "출발시간 없음")
            arrival = item.get("arrival", "도착시간 없음")
            duration = item.get("requiredtime", "소요시간 없음")
            seat_type = item.get("classes", "좌석 없음")
            onlinecnt = int(item.get("onlinecnt", 0))
            capacity = int(item.get("capacity", 0))

            key = (vessel, departure, arrival, duration)
            grouped.setdefault(key, []).append((seat_type, onlinecnt, capacity))

        lines = [f"🛳️ {date} 배편 현황"]
        for (vessel, dep, arr, duration), seats in grouped.items():
            lines.append(f"- {vessel} ({dep} → {arr} / {duration})")
            for seat_type, online, cap in seats:
                lines.append(f"  • {seat_type}석 (잔여 {online} / 정원 {cap})")

        return "\n".join(lines)

    except Exception as e:
        return f"❗ [{date}] 오류 발생: {e}"

# ✅ 실행
if __name__ == "__main__":
    dates = ["2025-08-30", "2025-09-13"]
    all_messages = []

    # 현재 시각 맨 위에 추가
