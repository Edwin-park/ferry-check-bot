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

def get_ferry_info(date: str, t_portid: str, f_portid: str, direction: str, title: str) -> str:
    # 방향별로 portsubid 설정
    if direction == "go":  # 강릉 → 울릉도
        t_subid = "1"
        f_subid = "0"
    elif direction == "return":  # 울릉도 → 강릉
        t_subid = "0"
        f_subid = "1"
    else:
        return f"❗ 잘못된 방향 지정: {direction}"

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
        "t_portsubidlist": t_subid,
        "t_portidlist": t_portid,
        "f_portsubidlist": f_subid,
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

if __name__ == "__main__":
    # (날짜, 출발지 ID, 도착지 ID, 방향, 설명)
    routes = [
        ("2025-09-13", "4311", "4406", "go", "가는 편: 강릉 → 울릉도"),
        ("2025-09-14", "4406", "4311", "return", "오는 편: 울릉도 → 강릉"),
        ("2025-09-15", "4406", "4311", "return", "오는 편: 울릉도 → 강릉"),
    ]

    all_messages = []
    for date, t_port, f_port, direction, title in routes:
        info = get_ferry_info(date, t_port, f_port, direction, title)
        all_messages.append(info)

    all_messages.append(
        "\n📌 설정\n"
        "• 가는 날: 2025-09-13 (강릉 → 울릉도)\n"
        "• 오는 날: 2025-09-14, 2025-09-15 (울릉도 → 강릉)"
    )

    final_message = "\n\n".join(all_messages)
    send_telegram_message(BOT_TOKEN, CHAT_ID, final_message)
