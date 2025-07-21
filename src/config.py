import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')

    # NewsAPI Configuration
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Report File Path
    REPORT_FILE_PATH = 'reports/hangar_fire_report.xlsx'