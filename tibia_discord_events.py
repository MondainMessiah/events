import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time

WEBHOOK_URL = "YOUR_WEBHOOK_URL"  # <-- Replace with your Discord webhook URL

def get_today_events():
    uk_tz = pytz.timezone('Europe/London')
    today = datetime.now(uk_tz)
    day = today.day

    url = "https://www.tibia.com/news/?subtopic=eventcalendar"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", {"id": "eventscheduletable"})
    if not table:
        return "Could not find the event table."

    events = []
    rows = table.find_all("tr")[1:]
    for row in rows:
        cells = row.find_all("td")
        for cell in cells:
            day_div = cell.find("div")
            if day_div:
                try:
                    cell_day = int(day_div.get_text(strip=True).split()[0])
                except Exception:
                    continue
                if cell_day == day:
                    for event_div in cell.find_all("div"):
                        text = event_div.get_text(strip=True)
                        if len(text) > 2 and not text.startswith(str(day)):
                            events.append(text)
                    for img in cell.find_all("img"):
                        alt = img.get('alt', '')
                        if alt:
                            events.append(alt)
                    for helper in cell.find_all("span", {"class": "HelperDivIndicator"}):
                        helper_title = helper.get("onmouseover", "")
                        if "font-size: 12pt;" in helper_title:
                            try:
                                desc_html = helper_title.split(", '', '")[1].replace("&quot;", '"')
                                desc = BeautifulSoup(desc_html, "html.parser").get_text(strip=True)
                                if desc:
                                    events.append(desc)
                            except Exception:
                                continue
    if not events:
        return "No events found for today."
    return "\n".join(events)

def post_to_discord(message):
    data = {"content": message}
    requests.post(WEBHOOK_URL, json=data)

def main():
    uk_tz = pytz.timezone('Europe/London')
    while True:
        now_uk = datetime.now(uk_tz)
        if now_uk.hour == 10 and now_uk.minute == 0:
            events = get_today_events()
            msg = f"**Events for today:**\n{events}"
            post_to_discord(msg)
            print(f"Posted at {now_uk.strftime('%Y-%m-%d %H:%M:%S')}")
            # Sleep for a minute to avoid posting twice in the same minute
            time.sleep(60)
        else:
            # Sleep for 30 seconds before checking again
            time.sleep(30)

if __name__ == "__main__":
    main()
