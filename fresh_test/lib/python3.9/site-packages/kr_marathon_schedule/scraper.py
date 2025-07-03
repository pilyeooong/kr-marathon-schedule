import requests
import json
import os
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime


class MarathonScraper:
    """Marathon schedule scraper for Korean running events."""
    
    def __init__(self, base_year: Optional[str] = None):
        """Initialize the scraper.
        
        Args:
            base_year: Year to scrape data for. Defaults to current year.
        """
        self.base_year = base_year or datetime.now().strftime("%Y")
        self.url = "http://www.roadrun.co.kr/schedule/list.php"
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
            
            event_name = cols[1].find("a").text.strip() if cols[1].find("a") else None
            if not event_name:
                continue
            
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
            
            marathon_data.append({
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
            })
        
        return marathon_data
    
    def scrape(self) -> List[Dict]:
        """Scrape marathon schedule data."""
        soup = self.fetch_html()
        table = self.parse_table(soup)
        
        if not table:
            raise ValueError("Could not find marathon schedule table")
        
        rows = table.find_all("tr")
        return self.extract_marathon_data(rows)
    
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


def get_marathons(year: Optional[str] = None) -> List[Dict]:
    """Get marathon schedule data for the specified year.
    
    Args:
        year: Year to get data for. Defaults to current year.
        
    Returns:
        List of marathon event dictionaries.
    """
    scraper = MarathonScraper(year)
    return scraper.scrape()