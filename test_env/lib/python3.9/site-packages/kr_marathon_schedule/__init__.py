"""
Korea Marathon Schedule Scraper

A Python package for scraping marathon and running event schedules in Korea.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .scraper import MarathonScraper, get_marathons

__all__ = ["MarathonScraper", "get_marathons"]