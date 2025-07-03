import argparse
import json
import csv
import sys
from typing import List, Dict
from .scraper import MarathonScraper


def save_csv(data: List[Dict], filepath: str) -> None:
    """Save marathon data to CSV file."""
    if not data:
        return
        
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape Korean marathon schedule data",
        prog="kr-marathon-schedule"
    )
    
    parser.add_argument(
        "--year", "-y",
        type=str,
        help="Year to scrape data for (default: current year)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory (default: marathon_data)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"Scraping marathon data for year: {args.year or 'current'}")
        
        scraper = MarathonScraper(args.year)
        data = scraper.scrape()
        
        if args.verbose:
            print(f"Found {len(data)} marathon events")
        
        output_dir = args.output or "marathon_data"
        
        if args.format == "json":
            filepath = scraper.save_json(data, output_dir)
            if args.verbose:
                print(f"Data saved to: {filepath}")
        elif args.format == "csv":
            import os
            from datetime import datetime
            
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filepath = os.path.join(output_dir, f"{timestamp}-marathon-schedule.csv")
            
            save_csv(data, filepath)
            if args.verbose:
                print(f"Data saved to: {filepath}")
        
        if not args.verbose:
            print(f"Successfully scraped {len(data)} marathon events")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()