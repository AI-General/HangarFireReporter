import datetime
import os
from typing import Any, Dict, List

from supabase import create_client
from tqdm import tqdm
from src.logging.colorlog_config import get_color_logger
from src.llm.hangarFireAnayser import HangarFireAnalyzer

# Use the color logger from the logging utility
logger = get_color_logger()

# Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError('Supabase credentials not set in environment variables.')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def article_upload(articles: List[Dict[str, Any]], is_backfill: bool) -> List[Dict[str, Any]]:
    """
    Uploads a list of articles to the database.
    """
    today = datetime.date.today()
    week_string = today.strftime("%G-W%V") if not is_backfill else "backfill"
    
    new_articles = []
    for article in tqdm(articles):
        analysis_result, query_embedding = HangarFireAnalyzer().analyze_article(article)
        if analysis_result.get("is_valid", False):
            if analysis_result["duplicate_index"] > 0:
                original_article = supabase.table('articles').select('*').eq('id', analysis_result["id"]).execute().data[0]
                if article.get('url') not in original_article.get('url', []):
                    original_article['url'].append(article.get('url', ''))
                if analysis_result.get('airport_hangar_name') and not original_article.get('airport_hangar_name'):
                    original_article['airport_hangar_name'] = analysis_result.get('airport_hangar_name')
                if analysis_result.get('country_region') and not original_article.get('location'):
                    original_article['location'] = analysis_result.get('country_region')
                supabase.table('articles').update(original_article).eq('id', analysis_result["id"]).execute()
            else:
                record = {
                    "title": article.get('title'),
                    "source": article.get('source'),
                    "publishedAt": article.get('publishedAt')[:10] if article.get('publishedAt') else None,
                    "location": analysis_result.get('country_region', ''),
                    "airport_hangar_name": analysis_result.get('airport_hangar_name', ''),
                    "author": article.get('author'),
                    "url": [article.get('url')],
                    "content": article.get('content'),
                    "embedding": query_embedding,
                    "collectedAt": week_string,
                }
                
                new_articles.append(record)
                supabase.table('articles').insert(record).execute()
    return new_articles