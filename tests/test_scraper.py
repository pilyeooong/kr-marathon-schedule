import pytest
from unittest.mock import Mock, patch
from kr_marathon_schedule.scraper import MarathonScraper, get_marathons


class TestMarathonScraper:
    """Test cases for MarathonScraper class."""
    
    def test_init_default_year(self):
        """Test scraper initialization with default year."""
        scraper = MarathonScraper()
        assert scraper.base_year is not None
        assert len(scraper.base_year) == 4
    
    def test_init_custom_year(self):
        """Test scraper initialization with custom year."""
        scraper = MarathonScraper("2023")
        assert scraper.base_year == "2023"
    
    @patch('kr_marathon_schedule.scraper.requests.post')
    def test_fetch_html(self, mock_post):
        """Test HTML fetching."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.apparent_encoding = "utf-8"
        mock_post.return_value = mock_response
        
        scraper = MarathonScraper()
        soup = scraper.fetch_html()
        
        assert soup is not None
        assert mock_post.called
    
    def test_extract_marathon_data_empty(self):
        """Test marathon data extraction with empty rows."""
        scraper = MarathonScraper()
        result = scraper.extract_marathon_data([])
        assert result == []
    
    def test_save_json_creates_files(self, tmp_path):
        """Test JSON file creation."""
        scraper = MarathonScraper()
        test_data = [{"event_name": "Test Marathon", "date": "1/1"}]
        
        filepath = scraper.save_json(test_data, str(tmp_path))
        
        assert filepath.endswith(".json")
        assert (tmp_path / "latest-marathon-schedule.json").exists()
    
    @patch('kr_marathon_schedule.scraper.MarathonScraper.scrape')
    def test_get_marathons(self, mock_scrape):
        """Test get_marathons function."""
        mock_scrape.return_value = [{"event_name": "Test Marathon"}]
        
        result = get_marathons()
        
        assert len(result) == 1
        assert result[0]["event_name"] == "Test Marathon"
        assert mock_scrape.called