import requests
import json
import os

from bs4 import BeautifulSoup
from datetime import datetime

BASE_YEAR = datetime.now().strftime("%Y")


def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    form_data = {
        "syear_key": BASE_YEAR,
    }
    response = requests.post(url, headers=headers, data=form_data)
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")

def parse_table(soup):
    tables = soup.find_all("table", {
        "width": "600",
        "border": "0",
        "bordercolor": "#000000",
        "cellpadding": "3",
        "cellspacing": "0"
    })
    
    return tables[1] if len(tables) > 1 else None

def extract_marathon_data(rows):
    marathon_data = []

    for row in rows:
        cols = row.find_all("td")

        fonts = cols[0].find_all("font")
        if not fonts:
            continue
        date = fonts[0].text.strip() if len(fonts) > 0 else None
        parts = date.split("/")
        month = int(parts[0]) if len(parts) > 0 else None
        day = int(parts[1]) if len(parts) > 1 else None
        day_of_week = fonts[1].text.strip("()") if len(fonts) > 1 else None

        event_name = cols[1].find("a").text.strip() if cols[1].find("a") else None
        if not event_name:
            continue
        
        tags_text = cols[1].find_all("font")[1].text.strip()

        tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []
        location = cols[2].find("div").text.strip()

        organizer_div = cols[3].find("div", align="right").text.strip()

        if "☎" in organizer_div:
            organizer_text, phone = organizer_div.split("☎", 1)
            phone = phone.strip()
        else:
            organizer_text = organizer_div.strip()
            phone = None

        organizer = [org.strip() for org in organizer_text.split(",")] if organizer_text else []

        marathon_data.append({
            "year": BASE_YEAR,
            "date": date,
            "month": month,
            "day": day,
            "day_of_week": day_of_week,
            "event_name": event_name,
            "tags": tags,
            "location": location,
            "organizer": organizer,
            "phone": phone
        })

    return marathon_data

def save_json(data):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}-marathon-schedule.json"

    save_folder = "marathon_data"
    os.makedirs(save_folder, exist_ok=True)

    filepath = os.path.join(save_folder, filename)
    latest_filepath = os.path.join(save_folder, "latest-marathon-schedule.json")

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    with open(latest_filepath, "w", encoding="utf-8") as latest_file:
        json.dump(data, latest_file, ensure_ascii=False, indent=4)

def main():
    url = "http://www.roadrun.co.kr/schedule/list.php"

    soup = fetch_html(url)
    table = parse_table(soup)
    
    if not table:
        print("테이블을 찾을 수 없습니다.")
        return

    rows = table.find_all("tr")
    marathon_json = extract_marathon_data(rows)
    save_json(marathon_json)

if __name__ == "__main__":
    main()
