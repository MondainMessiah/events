import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

WEBHOOK_URL = "https://discord.com/api/webhooks/1387871265028833441/9tzEU8A9TM2YvmkpzmkXNwFkqG4zQGo6wXvTYQEn5tqhA4TCAZ0yEiwnhLm4y3-MblJA"  # <-- Replace this with your Discord webhook URL

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

def already_ran_today():
    today = datetime.now(pytz.timezone('Europe/London')).strftime("%Y-%m-%d")
    try:
        with open("last_run.txt", "r") as f:
            last_run = f.read().strip()
        return last_run == today
    except FileNotFoundError:
        return False

def mark_ran_today():
    today = datetime.now(pytz.timezone('Europe/London')).strftime("%Y-%m-%d")
    with open("last_run.txt", "w") as f:
        f.write(today)

def main():
    if not already_ran_today():
        events = get_today_events()
        msg = f"**Events for today:**\n{events}"
        post_to_discord(msg)
        mark_ran_today()
        print("Posted events.")
    else:
        print("Already ran today.")

if __name__ == "__main__":
    main()
