import os
import requests

# 환경변수에서 봇 토큰과 채팅 ID 가져오기
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
        "t_portsubidlist": "1",    # 출발지: 강릉
        "t_portidlist": "4311",
        "f_portsubidlist": "0",    # 도착지: 울릉(저동)
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

        # 선박별로 묶기 (예: 일반/우등 같은 선박끼리)
        ferry_map = {}
        for item in result_all:
            vessel = item.get("vessel", "선박명 없음")
            departure = item.get("departure", "출발시간 없음")
            arrival = item.get("arrival", "도착시간 없음")
            duration = item.get("requiredtime", "")
            key = (vessel, departure, arrival, duration)

            if key not in ferry_map:
                ferry_map[key] = []
            ferry_map[key].append(item)

        lines = [f"🛳️ {date} 배편 현황"]
        for (vessel, dep, arr, dur), seats in ferry_map.items():
            lines.append(f"- {vessel} (강릉 {dep} → 울릉_저동 {arr} / {dur})")
            for s in seats:
                cls = s.get("classes", "좌석")
                online = int(s.get("onlinecnt", 0))
                cap = int(s.get("capacity", 0))
                lines.append(f"  • {cls}석 (잔여 {online} / 정원 {cap})")

        message = "\n".join(lines)
        send_telegram_message(BOT_TOKEN, CHAT_ID, message)

    except Exception as e:
        send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ [{date}] 오류 발생: {e}")

# ✅ 메인 실행부
if __name__ == "__main__":
    dates = ["2025-08-30", "2025-09-13"]  # 조회할 날짜
    for date in dates:
        check_ferry(date)
