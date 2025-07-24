import os
from src.llm.language import translate_query
from src.logging.colorlog_config import get_color_logger
from src.config import Config

# Configure colorful logging using Rich
from datetime import datetime, timedelta
from typing import List, Dict, Any
from serpapi import GoogleSearch

# Use the color logger from the logging utility
logger = get_color_logger()
config = Config()

class SerpScraper:
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY')
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not found in environment variables")

    def _is_old_article(self, date_str: str) -> bool:
        """Check if the Bing News date string is valid for the current mode (backfill or weekly)"""
        if not date_str:
            logger.warning("Empty date string provided")
            return True
        if date_str.endswith('y') and int(date_str[:-1]) > 5:
            return True
        else: 
            return False

    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        try:
            for article in articles:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_articles.append(article)
            return unique_articles
        
        except Exception as e:
            logger.error(f"Error removing duplicates: {str(e)}")
            return articles

    def _parse_date(self, date_str: str) -> str:
        """Parse and format date string for both absolute and relative formats"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        try:
            # Handle relative date formats (Bing News)
            now = datetime.now()
            if date_str.endswith('m'):
                return now.strftime('%Y-%m-%d')
            elif date_str.endswith('h'):
                hours = int(date_str[:-1])
                parsed_date = now - timedelta(hours=hours)
                return parsed_date.strftime('%Y-%m-%d')
            elif date_str.endswith('d'):
                days = int(date_str[:-1])
                parsed_date = now - timedelta(days=days)
                return parsed_date.strftime('%Y-%m-%d')
            elif date_str.endswith('mon'):
                months = int(date_str[:-3])
                parsed_date = now - timedelta(days=months*30)
                return parsed_date.strftime('%Y-%m-%d')
            elif date_str.endswith('y'):
                years = int(date_str[:-1])
                parsed_date = now - timedelta(days=years*365)
                return parsed_date.strftime('%Y-%m-%d')
            # Handle absolute date formats (Google News)
            date_formats = [
                '%m/%d/%Y, %I:%M %p, +0000 UTC',  # 04/19/2012, 07:00 AM, +0000 UTC
                '%m/%d/%Y, %I:%M %p',  # 11/12/2024, 09:03 AM
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y'
            ]
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            # If no format matches, return current date
            return datetime.now().strftime('%Y-%m-%d')
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')

    def search_google_news(self, query: str, weekly: bool = False, language: str = 'en') -> List[Dict[str, Any]]:
        """Search Google News for query"""
        try:
            params = {
                "engine": "google_news",
                "q": query,
                "api_key": self.api_key,
                "hl": language
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "news_results" in results:
                temp_articles = [{
                    "title": article.get("title"),
                    "url": article.get("link"),
                    "description": None,
                    "source": article.get("source").get("name"),
                    "author": ",".join(article.get("source").get("authors")) if article.get("source").get("authors") else article.get("source").get("authors"),
                    "publishedAt": self._parse_date(article.get("date")),
                    "language": language,
                } for article in results["news_results"]]
                
                if weekly:
                    today = datetime.today()
                    # Find this week's Monday
                    this_week_start = today - timedelta(days=today.weekday())
                    # Go back 7 days to last week's Monday
                    last_week_start = this_week_start - timedelta(days=7)
                    final_articles = [article for article in temp_articles if datetime.strptime(article['publishedAt'], '%Y-%m-%d') >= last_week_start]
                    return final_articles
                else:
                    return temp_articles
                
            else:
                if "error" in results:
                    logger.error(f"Error in search results for query '{query}': {results['error']}")
                else:
                    logger.warning(f"No news results found for query: {query}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Google News for query '{query}': {str(e)}")
            return []

    def search_bing_news(self, query: str, weekly: bool = False, language: str = 'en') -> List[Dict[str, Any]]:
        """Search Bing News for MRO hangar projects with pagination and date range check"""
        try:
            params = {
                "engine": "bing_news",
                "q": query,
                "api_key": self.api_key,
                "count": 10, # Number of results per page
                'qft': 'interval="8"+sortbydate="1"' if weekly else 'sortbydate="1"'
            }

            all_articles = []
            first = 1
            stop_paging = False
            while not stop_paging:
                params['first'] = first
                search = GoogleSearch(params)
                results = search.get_dict()
                organic_results = results.get("organic_results", [])
                if not organic_results:
                    break
                for article in organic_results:
                    date_str = article.get('date', '')
                    is_old_article = self._is_old_article(date_str)
                    if is_old_article:
                        stop_paging = True
                        break
                    all_articles.append(article)
                if stop_paging or len(organic_results) < params['count']:
                    break
                first += params['count']
            return [{
                "title": article.get("title"),
                "url": article.get("link"),
                "description": article.get("snippet"),
                "source": article.get("source"),
                "author": None,
                "publishedAt": self._parse_date(article.get("date")),
                "language": language
            } for article in all_articles]
        except Exception as e:
            logger.error(f"Error searching Bing News for query '{query}': {str(e)}")
            return []

    def scrape(self, query_list: List[str], weekly: bool = False) -> List[Dict[str, Any]]:
        """Scrape all news sources"""
        all_articles = []

        for language in config.LANGUAGES:
            logger.info(f"##### Starting Scraping news for language: {language} #####")
            for query in query_list:
                query_lng = translate_query(query, language)
                logger.info(f"Searching for query: {query_lng}")

                # Search Bing News
                bing_results = self.search_bing_news(query_lng, weekly=weekly, language=language)
                all_articles.extend(bing_results)
                
                # Search Google News
                google_results = self.search_google_news(query_lng, weekly=weekly, language=language)
                all_articles.extend(google_results)
        
        # Remove duplicates based on URL
        unique_articles = self._remove_duplicates(all_articles)
        logger.info(f"Found {len(unique_articles)} unique articles with SERP API.")
        return unique_articles
    