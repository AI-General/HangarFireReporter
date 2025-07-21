import os
import dotenv
import datetime
import json
import sys
from src.logging.colorlog_config import get_color_logger
from src.parser.doc import doc_parse
from src.scrapers.scrape_newsapi import get_articles_from_newsapi
from src.scrapers.scrape_serpapi import SerpScraper
from src.db import doc_upload, clean_database, get_articles, get_similar_articles
from src.db.upload import article_upload
from src.excel.article_excel_exporter import ArticleExcelExporter
from src.email_sender import EmailSender
from src.scheduler import ScrapingScheduler
from src.config import Config

logger = get_color_logger()

email_sender = EmailSender()
scheduler = ScrapingScheduler()
config = Config()

def weekly_process():
    query_list = [
        'aircraft hangar fire',
        'MRO facility fire',
        'aviation hangar fire',
        'aircraft maintenance hangar fire'
    ]
    scraper = SerpScraper()
    articles = scraper.scrape(query_list=query_list, weekly=True)
    
    new_articles = article_upload(articles, is_backfill=False)
    logger.info(f"Uploaded {len(new_articles)} new articles to Supabase.")

    if len(new_articles) > 0:
        exporter = ArticleExcelExporter()
        exporter.export_articles_to_excel()

    email_success = email_sender.send_report_email(
        filepath=config.REPORT_FILE_PATH, article_count=len(new_articles)
    )
    if email_success:
        logger.info("Weekly report email sent successfully.")
    else:
        logger.error("Failed to send weekly report email.")

def email_sender_test():
    filepath = config.REPORT_FILE_PATH
    article_count = 0  # Example count, replace with actual count if needed
    recipient_email = os.getenv('RECIPIENT_EMAIL')  # Replace with actual recipient email
    
    email_success = email_sender.send_report_email(filepath, article_count, recipient_email)
    logger.info(f"Email sent: {'Success' if email_success else 'Failed'}")




if __name__ == "__main__":
    dotenv.load_dotenv()  # Load environment variables from .env file
    if len(sys.argv) < 2:
        logger.error("Usage: python main.py <option>")
        sys.exit(1)
       
    option = sys.argv[1].lower()
    
    if option == "scrape_newsapi" or option == "0":
        query = '(aircraft hangar fire) OR (MRO facility fire) OR (aviation hangar fire) OR (aircraft maintenance hangar fire)'
        today = datetime.datetime.utcnow()
        from_date = (today - datetime.timedelta(days=20)).strftime('%Y-%m-%d')
        articles = get_articles_from_newsapi(query, from_date)
        with open("temp/newsapi_articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        new_articles = article_upload(articles, is_backfill=False)
        logger.info(f"Uploaded {len(new_articles)} new articles to Supabase.")

    elif option == "weekly":
        weekly_process()

    elif option == "scrape_serpapi" or option == "1":
        query_list = [
            'aircraft hangar fire',
            'MRO facility fire',
            'aviation hangar fire',
            'aircraft maintenance hangar fire'
        ]
        scraper = SerpScraper()
        articles = scraper.scrape(query_list=query_list)
        with open("temp/serpapi_articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"Scraped {len(articles)} articles and saved to serpapi_articles.json.")
    
    elif option == "doc_parse" or option == "2":
        file_path = "data/history.docx"  # Replace with your document path
        articles = doc_parse(file_path)
        with open("temp/doc_articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"Parsed {len(articles)} articles and saved to doc_articles.json.")
        
    elif option == "doc_upload" or option == "3":
        clean_database("articles")
        file_path = "temp/doc_articles.json"
        doc_upload(file_path)

    elif option == "test_similarity" or option == "4":
        query = "aircraft hangar fire"
        similar_articles = get_similar_articles(query, limit=2)
        print(f"Found {len(similar_articles)} similar articles for query '{query}':")
        for article in similar_articles:
            print(f"- {article['title']} (Similarity: {article['similarity']})")
    
    elif option == "test_analyzer" or option == "5":
        from src.llm.hangarFireAnayser import HangarFireAnalyzer
        
        article =   {
            "title": "Hangar roof collapses, planes destroyed in Greenville Downtown Airport fire",
            "url": "https://www.foxcarolina.com/2023/11/13/live-crews-responding-fire-greenville-downtown-airport/",
            "source": "FOX Carolina",
            "author": "Anisa Snipes",
            "publishedAt": "2023-11-13"
        }

        analyzer = HangarFireAnalyzer()
        analyzer.analyze_article(article=article)
    
    elif option == "backfill" or option == "6":
        file_path = "temp/serpapi_articles.json"
        with open(file_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        new_articles = article_upload(articles, is_backfill=True)
        with open("temp/backfill_articles.json", "w", encoding="utf-8") as f:
            json.dump(new_articles, f, ensure_ascii=False, indent=2)
        print(f"Uploaded {len(new_articles)} new articles to Supabase.")
    
    elif option == "backfill_excel" or option == "7":
        exporter = ArticleExcelExporter()
        exporter.export_articles_to_excel()
    
    elif option == "email_test" or option == "8":
        email_sender_test()
    
    elif option == "schedule" or option == "9":
        scheduler.schedule_weekly_run(weekly_process)
        scheduler.run_scheduler()
    
    else:
        print(f"Unknown option: {option}")
