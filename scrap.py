import requests
import json
import os
import re
import argparse

from bs4 import BeautifulSoup
from datetime import datetime

TARGET_YEARS = ["2025", "2026"]


def fetch_html(url, year):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    form_data = {
        "syear_key": year,
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

def extract_marathon_data(rows, year):
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

        event_name_link = cols[1].find("a")
        event_name = event_name_link.text.strip() if event_name_link else None
        if not event_name:
            continue

        event_id = None
        if event_name_link and event_name_link.get("href"):
            href = event_name_link.get("href")
            match = re.search(r"'view\.php\?no=(\d+)'", href)
            if match:
                event_id = match.group(1)

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

        homepage = None
        home_img = cols[3].find("img", src=lambda s: s and "home.gif" in s)
        if home_img and home_img.parent and home_img.parent.name == "a":
            href = home_img.parent.get("href", "")
            if href and not href.startswith("javascript:"):
                homepage = href

        email = None
        email_img = cols[3].find("img", src=lambda s: s and "email.gif" in s)
        if email_img and email_img.parent and email_img.parent.name == "a":
            href = email_img.parent.get("href", "")
            mail_match = re.search(r"mail_url=([^'\"&]+)", href)
            if mail_match:
                email = mail_match.group(1)

        data = {
            "year": year,
            "date": date,
            "month": month,
            "day": day,
            "day_of_week": day_of_week,
            "event_name": event_name,
            "tags": tags,
            "location": location,
            "organizer": organizer,
            "phone": phone
        }
        if event_id:
            data["event_id"] = event_id
        if homepage:
            data["homepage"] = homepage
        if email:
            data["email"] = email

        marathon_data.append(data)

    return marathon_data

def fetch_detail_data(event_id, headers):
    """상세 페이지에서 GPS 좌표, 지도주소, 지역 추출"""
    url = f"http://www.roadrun.co.kr/schedule/view.php?no={event_id}"
    try:
        import time
        time.sleep(0.5)
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")

        detail = {}

        scripts = soup.find_all("script")
        for script in scripts:
            text = script.string or ""
            coord_match = re.search(r"naver\.maps\.LatLng\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)", text)
            if coord_match:
                detail["latitude"] = float(coord_match.group(1))
                detail["longitude"] = float(coord_match.group(2))

            if "contentString" in text:
                parts = re.findall(r"'([^']*)'", text[text.index("contentString"):text.index(".join")] if ".join" in text else "")
                addr_text = re.sub(r"<[^>]+>", "", "".join(parts)).strip()
                if addr_text:
                    detail["map_address"] = addr_text

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    header = cells[0].get_text(strip=True)
                    if "대회지역" in header:
                        detail["region"] = cells[1].get_text(strip=True)

        return detail
    except Exception as e:
        print(f"Error fetching detail for event {event_id}: {e}")
        return {}


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
    parser = argparse.ArgumentParser(description="마라톤 대회 일정 크롤러")
    parser.add_argument("--detail", action="store_true",
                        help="상세 페이지에서 GPS 좌표, 지도주소, 지역 정보 추가 수집")
    args = parser.parse_args()

    url = "http://www.roadrun.co.kr/schedule/list.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    all_marathon_data = []

    for year in TARGET_YEARS:
        soup = fetch_html(url, year)
        table = parse_table(soup)

        if not table:
            print(f"{year}년 테이블을 찾을 수 없습니다.")
            continue

        rows = table.find_all("tr")
        year_data = extract_marathon_data(rows, year)
        all_marathon_data.extend(year_data)
        print(f"{year}년: {len(year_data)}개 대회 수집")

    if args.detail:
        print("상세 페이지 크롤링 시작...")
        for i, event in enumerate(all_marathon_data):
            event_id = event.get("event_id")
            if event_id:
                detail = fetch_detail_data(event_id, headers)
                event.update(detail)
                if (i + 1) % 10 == 0:
                    print(f"  {i + 1}/{len(all_marathon_data)} 처리 완료")
        print("상세 페이지 크롤링 완료")

    if all_marathon_data:
        all_marathon_data.sort(key=lambda x: (x["year"], x["month"], x["day"]))
        save_json(all_marathon_data)
        print(f"총 {len(all_marathon_data)}개 대회 저장 완료")

if __name__ == "__main__":
    main()
