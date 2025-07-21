import os
from typing import List, Dict, Any
from supabase import create_client
import json
from src.llm import get_embedding
from src.logging.colorlog_config import get_color_logger

# Use the color logger from the logging utility
logger = get_color_logger()

# Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError('Supabase credentials not set in environment variables.')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
def clean_database(db_name: str) -> None:
    """
    Cleans the database by dropping the specified table if it exists.
    
    Args:
        db_name (str): Name of the database to clean.
    """
    # Drop the table if it exists
    supabase.table(db_name).delete().gte("id", 0).execute()


def doc_upload(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads a JSON file containing a list of articles and uploads them to the 'articles' table in Supabase.
    Returns the list of inserted records.
    """
    # Read JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
        
    if not isinstance(articles, list):
        raise ValueError('JSON file must contain a list of articles.')

    # Generate embeddings and add to each article
    for article in articles:
        # Combine title and content (adjust fields as needed)
        combined_text = f"""Title: {article.get('title', '')}
Location: {article.get('location', "")}
Published At: {article.get('publishedAt', "")}
Content: {article.get('content', "")}""".strip()

        if not combined_text:
            raise ValueError('Article missing title and content for embedding.')

        article['embedding'] = get_embedding(combined_text)
        article["collectedAt"] = "doc"

        if isinstance(article.get('url'), str): article['url'] = [article.get('url')]

    # Upload to Supabase
    response = supabase.table('articles').insert(articles).execute()
    # Use dict-style access for error/data only
    if isinstance(response, dict):
        if response.get('error'):
            raise Exception(f"Supabase insert error: {response['error']}")
        return response.get('data', [])
    return [] 


def get_similar_articles(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieves similar articles based on the query using the 'articles' table in Supabase.
    
    Args:
        query (str): The search query to find similar articles.
        limit (int): The maximum number of articles to return.
    
    Returns:
        List[Dict[str, Any]]: List of similar articles.
    """
    # Get embedding for the query
    query_embedding = get_embedding(query)
    
    # Query the database for similar articles
    response = supabase.rpc('match_articles', {'query_embedding': query_embedding, 'match_count': limit}).execute()
    if response.data:
        return response.data, query_embedding
    elif response.error:
        raise Exception(f"Supabase query error: {response.error}")
    return []


def get_articles() -> List[Dict[str, Any]]:
    """
    Retrieves articles from the 'articles' table in Supabase for a specific week.

    Returns:
        List[Dict[str, Any]]: List of articles for the specified week.
    """
    response = supabase.table('articles').select('*').neq('collectedAt', 'doc').execute()
    if response.data:
        return response.data
    elif response.error:
        raise Exception(f"Supabase query error: {response.error}")
    return []