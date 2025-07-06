import os
import warnings

# SSL 경고 무시 (import 전에 설정)
os.environ['PYTHONWARNINGS'] = 'ignore::urllib3.exceptions.InsecureRequestWarning'
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')
warnings.filterwarnings('ignore', category=UserWarning, module='urllib3')

import requests
import json
import time
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import urllib3

# 추가 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3.disable_warnings()


class MarathonScraper:
    """Marathon schedule scraper for Korean running events."""
    
    def __init__(self, base_year: Optional[str] = None, fetch_details: bool = True):
        """Initialize the scraper.
        
        Args:
            base_year: Year to scrape data for. Defaults to current year.
            fetch_details: Whether to fetch detailed information from individual pages.
        """
        self.base_year = base_year or datetime.now().strftime("%Y")
        self.url = "http://www.roadrun.co.kr/schedule/list.php"
        self.base_url = "http://www.roadrun.co.kr"
        self.fetch_details = fetch_details
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def fetch_html(self) -> BeautifulSoup:
        """Fetch HTML content from the marathon schedule website."""
        form_data = {"syear_key": self.base_year}
        response = requests.post(self.url, headers=self.headers, data=form_data)
        response.encoding = response.apparent_encoding
        return BeautifulSoup(response.text, "html.parser")
    
    def parse_table(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Parse the marathon schedule table from HTML."""
        tables = soup.find_all("table", {
            "width": "600",
            "border": "0",
            "bordercolor": "#000000",
            "cellpadding": "3",
            "cellspacing": "0"
        })
        return tables[1] if len(tables) > 1 else None
    
    def extract_marathon_data(self, rows) -> List[Dict]:
        """Extract marathon data from table rows."""
        marathon_data = []
        
        for row in rows:
            cols = row.find_all("td")
            
            fonts = cols[0].find_all("font")
            if not fonts:
                continue
                
            date = fonts[0].text.strip() if len(fonts) > 0 else None
            if not date:
                continue
                
            parts = date.split("/")
            month = int(parts[0]) if len(parts) > 0 else None
            day = int(parts[1]) if len(parts) > 1 else None
            day_of_week = fonts[1].text.strip("()") if len(fonts) > 1 else None
            
            event_name_link = cols[1].find("a")
            event_name = event_name_link.text.strip() if event_name_link else None
            if not event_name:
                continue
            
            detail_url = None
            if event_name_link and event_name_link.get("href"):
                href = event_name_link.get("href")
                if href.startswith("javascript:open_window"):
                    match = re.search(r"'view\.php\?no=(\d+)'", href)
                    if match:
                        detail_url = f"schedule/view.php?no={match.group(1)}"
            
            tags_text = cols[1].find_all("font")[1].text.strip() if len(cols[1].find_all("font")) > 1 else ""
            tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []
            
            location = cols[2].find("div").text.strip() if cols[2].find("div") else ""
            
            organizer_div = cols[3].find("div", align="right")
            organizer_text = organizer_div.text.strip() if organizer_div else ""
            
            if "☎" in organizer_text:
                organizer_text, phone = organizer_text.split("☎", 1)
                phone = phone.strip()
            else:
                phone = None
            
            organizer = [org.strip() for org in organizer_text.split(",")] if organizer_text else []
            
            base_data = {
                "year": self.base_year,
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
            
            if detail_url and self.fetch_details:
                detail_data = self.fetch_detail_data(detail_url)
                base_data.update(detail_data)
            
            marathon_data.append(base_data)
        
        return marathon_data
    
    def fetch_detail_data(self, detail_url: str) -> Dict:
        """Fetch additional data from detail page."""
        if not detail_url:
            return {}
        
        try:
            time.sleep(0.5)
            
            full_url = urljoin(self.base_url, detail_url)
            
            response = requests.get(full_url, headers=self.headers, verify=False, timeout=10)
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            detail_data = {}
            
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        header = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        if "대표자" in header:
                            detail_data["representative"] = value
                        elif "E-mail" in header:
                            detail_data["email"] = value
                        elif "출발시간" in header:
                            detail_data["start_time"] = value
                        elif "접수기간" in header:
                            detail_data["registration_period"] = value
                        elif "홈페이지" in header:
                            detail_data["homepage"] = value
                        elif "기타소개" in header:
                            detail_data["description"] = value
                        elif "대회장" in header and "대회장소" not in header:
                            detail_data["venue_detail"] = value
            
            return detail_data
            
        except Exception as e:
            print(f"Error fetching detail data from {detail_url}: {e}")
            return {}
    
    def scrape(self) -> List[Dict]:
        """Scrape marathon schedule data."""
        soup = self.fetch_html()
        table = self.parse_table(soup)
        
        if not table:
            raise ValueError("Could not find marathon schedule table")
        
        rows = table.find_all("tr")
        return self.extract_marathon_data(rows)
    
    def get_event_detail(self, event_id: str) -> Dict:
        """Get detailed information for a specific event."""
        detail_url = f"schedule/view.php?no={event_id}"
        return self.fetch_detail_data(detail_url)
    
    def save_json(self, data: List[Dict], output_dir: str = "marathon_data") -> str:
        """Save marathon data to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}-marathon-schedule.json"
        
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        latest_filepath = os.path.join(output_dir, "latest-marathon-schedule.json")
        
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        with open(latest_filepath, "w", encoding="utf-8") as latest_file:
            json.dump(data, latest_file, ensure_ascii=False, indent=4)
        
        return filepath


def get_marathons(year: Optional[str] = None, fetch_details: bool = True) -> List[Dict]:
    """Get marathon schedule data for the specified year.
    
    Args:
        year: Year to get data for. Defaults to current year.
        fetch_details: Whether to fetch detailed information from individual pages.
        
    Returns:
        List of marathon event dictionaries.
    """
    scraper = MarathonScraper(year, fetch_details)
    return scraper.scrape()