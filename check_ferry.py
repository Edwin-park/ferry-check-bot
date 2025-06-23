import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    res = requests.post(url, data=payload)
    print("텔레그램 응답:", res.text)

def check_ferry(date):
    url = "https://island.theksa.co.kr/booking/selectDepartureList"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json",
        "Origin": "https://island.theksa.co.kr",
        "Referer": "https://island.theksa.co.kr/",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {
        "masterdate": date,
        "t_portsubidlist": "1",      # 출발: 강릉
        "t_portidlist": "4311",
        "f_portsubidlist": "0",      # 도착: 울릉 저동
        "f_portidlist": "4406",
        "lang": "ko",
        "sourcesiteid": "1PHSOBKSACLAIOD1XZMZ"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("data", {}).get("resultAll", [])

if __name__ == "__main__":
    date = "2025-08-30"
    results = check_ferry(date)

    if not results:
        send_telegram_message(BOT_TOKEN, CHAT_ID, f"❗ {date} 배편 정보가 없습니다.")
    else:
        for r in results:
            msg = f"""🛳️ 배편 정보 ({date})
{r.get('depportname', '출발지 없음')} → {r.get('arrportname', '도착지 없음')} ({r.get('shipname', '선박명 없음')})
출발 시간: {r.get('depplandate', date)} {r.get('depplantime', '시간 없음')}
잔여석: {r.get('remcnt', '미표시')}석"""
            send_telegram_message(BOT_TOKEN, CHAT_ID, msg)
