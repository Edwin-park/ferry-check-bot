import os
import requests

# 환경변수에서 BOT_TOKEN, CHAT_ID 가져오기
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

# 날짜별 배편 정보 조회 함수
def get_ferry_info(date: str, t_portid: str, f_portid: str, title: str) -> str:
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
        "t_portidlist": t_portid,
        "f_portsubidlist": "0",
        "f_portidlist": f_portid,
        "lang": "ko",
        "sourcesiteid": "1PHSOBKSACLAIOD1XZMZ"
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result_all = response.json().get("data", {}).get("resultAll", [])

        if not result_all:
            return f"\n🛳️ {title} ({date})\n• 배편 없음"

        grouped = {}
        for item in result_all:
            vessel = item.get("vessel", "선박명 없음")
            departure = item.get("departure", "출발지 없음")
            arrival = item.get("arrival", "도착지 없음")
            duration = item.get("requiredtime", "소요시간 없음")
            seat_type = item.get("classes", "좌석 없음")
            onlinecnt = int(item.get("onlinecnt", 0))
            capacity = int(item.get("capacity", 0))

            key = (vessel, departure, arrival, duration)
            grouped.setdefault(key, []).append((seat_type, onlinecnt, capacity))

        lines = [f"🛳️ {title} ({date})"]
        for (vessel, dep, arr, duration), seats in grouped.items():
            lines.append(f"- {vessel} ({dep} → {arr} / {duration})")
            for seat_type, online, cap in seats:
                lines.append(f"  • {seat_type} (잔여 {online} / 정원 {cap})")

        return "\n".join(lines)

    except Exception as e:
        return f"❗ {title} ({date}) 오류 발생: {e}"

# 메인 실행
if __name__ == "__main__":
    # 날짜 및 방향 설정: (날짜, 출발지 ID, 도착지 ID, 제목)
    routes = [
        ("2025-09-13", "4311", "4406", "가는 편: 강릉 → 울릉도"),
        ("2025-09-15", "4406", "4311", "오는 편: 울릉도 → 강릉"),
    ]

    all_messages = []
    for date, t_port, f_port, title in routes:
        info = get_ferry_info(date, t_port, f_port, title)
        all_messages.append(info)

    # 설정 정보 추가
    all_messages.append("\n📌 설정\n• 가는 날: 2025-09-13 (강릉 → 울릉도)\n• 오는 날: 2025-09-15 (울릉도 → 강릉)")

    # 텔레그램 전송
    final_message = "\n\n".join(all_messages)
    send_telegram_message(BOT_TOKEN, CHAT_ID, final_message)
