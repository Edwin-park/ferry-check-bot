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

# 배편 조회 함수
def check_ferry(date_list):
    url = "https://island.theksa.co.kr/booking/selectDepartureList"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://island.theksa.co.kr",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://island.theksa.co.kr/",
        "X-Requested-With": "XMLHttpRequest"
    }

    summary_lines = []
    sep13_found = False

    for date in date_list:
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

            if date == "2025-09-13" and result_all:
                sep13_found = True

            if not result_all:
                continue

            lines = [f"🚣️ {date} 배편 현황"]
            route_groups = {}

            for item in result_all:
                vessel = item.get("vessel", "선박명 없음")
                seat_class = item.get("classes", "자리 없음")
                departure = item.get("f_port", "출발지 없음") + " " + item.get("departure", "시간 없음")
                arrival = item.get("t_port", "도착지 없음") + " " + item.get("arrival", "시간 없음")
                duration = item.get("requiredtime", "소요시간 없음")
                onlinecnt = int(item.get("onlinecnt", 0))
                capacity = int(item.get("capacity", 0))

                key = (vessel, departure, arrival, duration)
                if key not in route_groups:
                    route_groups[key] = []
                route_groups[key].append((seat_class, onlinecnt, capacity))

            for (vessel, departure, arrival, duration), seats in route_groups.items():
                lines.append(f"- {vessel} ({departure} → {arrival} / {duration})")
                for seat_class, onlinecnt, capacity in seats:
                    lines.append(f"  • {seat_class} (잔여 {onlinecnt} / 정원 {capacity})")

            summary_lines.extend(lines)

        except Exception as e:
            send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ [{date}] 오류 발생: {e}")

    # 현재 시간 출력
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M")

    # 날짜 순서 정렬
    ordered_dates = ["2025-08-30", "2025-09-13"]
    summary_lines_ordered = []
    for date in ordered_dates:
        summary_lines_for_date = [
            line for line in summary_lines 
            if line.startswith(f"🚣️ {date}") or line.startswith("- ") or line.startswith("  •")
        ]
        if summary_lines_for_date:
            summary_lines_ordered.extend(summary_lines_for_date)

    # 메시지 전송 조건
    minute = now.minute
    should_send = True
    if sep13_found:
        should_send = True
    elif minute == 0:
        should_send = True

    if should_send:
        current_time = f"📆 현재시간: {now_str}"
        setting = (
            "\n\n📌 설정\n"
            "• 날짜: 2025-08-30, 2025-09-13\n"
            "• 작동 시간: 24시간"
        )
        message = current_time + "\n\n" + "\n".join(summary_lines_ordered) + setting
        send_telegram_message(BOT_TOKEN, CHAT_ID, message)

# ✅ 실행 부분
if __name__ == "__main__":
    check_ferry(["2025-08-30", "2025-09-13"])
