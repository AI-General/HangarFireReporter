import datetime
import json
import sys
from src.scrapers.scrape_newsapi import get_articles_from_newsapi
from src.scrapers.scrape_serpapi import SerpScraper

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <option>")
        sys.exit(1)
    
    # query = 'aircraft hangar fire'
    
    option = sys.argv[1].lower()
    
    if option == "scrape_newsapi":
        query = '(aircraft hangar fire) OR (MRO facility fire) OR (aviation hangar fire) OR (aircraft maintenance hangar fire)'
        today = datetime.datetime.utcnow()
        from_date = (today - datetime.timedelta(days=8)).strftime('%Y-%m-%d')
        articles = get_articles_from_newsapi(query, from_date)
        with open("newsapi_articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"Scraped {len(articles)} articles and saved to articles.json.")
    
    if option == "scrape_serpapi":
        # query_list = [
        #     'aircraft hangar fire',
        #     'MRO facility fire',
        #     'aviation hangar fire',
        #     'aircraft maintenance hangar fire'
        # ]
        query_list = [
            'aircraft hangar fire'
        ]
        scraper = SerpScraper()
        articles = scraper.scrape(query_list=query_list)
        with open("serpapi_articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"Scraped {len(articles)} articles and saved to serpapi_articles.json.")  
    
    else:
        print(f"Unknown option: {option}")
