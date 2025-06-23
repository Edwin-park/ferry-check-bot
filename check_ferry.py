import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, data=payload)

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
        "masterdate": date,              # 날짜를 여기에 전달
        "t_portsubidlist": "1",          # 출발: 강릉
        "t_portidlist": "4311",
        "f_portsubidlist": "0",          # 도착: 울릉 저동
        "f_portidlist": "4406",
        "lang": "ko",
        "sourcesiteid": "1PHSOBKSACLAIOD1XZMZ"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("data", {}).get("resultAll", [])

if __name__ == "__main__":
    # ✅ 고정된 날짜로 체크: 2025년 8월 30일
    date = "2025-08-30"
    results = check_ferry(date)
    for r in results:
        if int(r.get("remcnt", 0)) > 0:
            msg = f"""🚢 배표 있음!
{r['depplandate']} {r['depplantime']}
{r['depportname']} → {r['arrportname']} ({r['shipname']})
잔여석: {r['remcnt']}석"""
            send_telegram_message(BOT_TOKEN, CHAT_ID, msg)
