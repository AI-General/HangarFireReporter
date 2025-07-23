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

    SCHEDULE_TIME = '08:00'
    SCHEDULE_DAY = 'tuesday'
    
    query_list = [
        'aircraft hangar fire',
        'MRO facility fire',
        'aviation hangar fire',
        'aircraft maintenance hangar fire',
        'foam suppression system malfunction',
        'AFFF accidental discharge',
        'foam fire suppression system malfunction'
    ]
    
    LANGUAGES = [
        # 'en',
        'zh-cn',
        'es',
        'fr',
        'pt',
        'de',
        'ar',
        'ru',
        'jp',
        'tr'
    ]