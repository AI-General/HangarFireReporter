import requests
import os
from dotenv import load_dotenv

load_dotenv()
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

PAGE_SIZE = 100


def get_articles_from_newsapi(query, from_date):
    base_url = 'https://newsapi.org/v2/everything'
    headers = {'Authorization': NEWSAPI_KEY}
    
    all_articles = []
    page = 1
    total_results = 1  # dummy to enter loop
    
    while len(all_articles) < total_results:
        params = {
            'q': query,
            'pageSize': PAGE_SIZE,
            'page': page,
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date
        }
        response = requests.get(base_url, headers=headers, params=params)
        data = response.json()
        if response.status_code != 200 or 'articles' not in data:
            print(f"Error fetching page {page}: {data}")
            break
        if page == 1:
            total_results = min(data.get('totalResults', 0), 100 * 5)  # NewsAPI caps at 100 results per page, 5 pages max
        all_articles.extend(data['articles'])
        if len(data['articles']) < PAGE_SIZE:
            break  # No more articles
        page += 1
        if page > 5:
            break  # NewsAPI free tier limit
    return all_articles
