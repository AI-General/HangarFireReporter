import json
import os
from typing import Dict, List, Any
import openai

from src.db import get_similar_articles


class HangarFireAnalyzer:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=api_key)

    def create_analysis_prompt(self, existing_articles: List[Dict], new_article: Dict) -> str:
        """
        Create a prompt for analyzing the new article against existing articles.
        """
        prompt = f"""You are an expert analyst specializing in aviation hangar fire incidents. Your task is to analyze a new article and provide structured information about it.

EXISTING ARTICLES FOR COMPARISON:
"""
        for i, article in enumerate(existing_articles):
            prompt += f"""
Article {i + 1}:
Title: {article.get('title', '')}
Article Date: {article.get('publishedAt', '')}
Article Links: {str(article.get('url', ''))}
Location: {article.get('location', '')}
Description: {article.get('description', '')}
Content: {article.get('content', '')}
"""
        prompt += f"""
NEW ARTICLE TO ANALYZE:
Title: {new_article.get('title', '')}
Article Date: {new_article.get('publishedAt', '')}
Article Links: {str(new_article.get('url', ''))}
Location: {new_article.get('location', '')}
Description: {new_article.get('description', '')}
Content: {new_article.get('content', '')}
"""
        prompt += f"""
ANALYSIS REQUIREMENTS:

1. **is_valid** (boolean):
   Include ONLY incidents that meet ALL of the following criteria:
   • Occurred in ACTIVE aircraft hangars (MRO, commercial, or military aviation)
   • Fire originated in OR affected the hangar structure or operations
   • Direct involvement of aircraft is noted, OR facility functions support aviation activity
   • Includes incidents involving malfunctioning or accidental discharge of foam fire suppression systems (e.g., AFFF, High Expansion foam, fire retardant foam) that directly impacts the facility or aircraft
   
   EXCLUDE:
   • Fires in repurposed or historic hangars (museums, galleries, event spaces)
   • Fires in storage-only buildings with no aircraft activity
   • Non-fire-related incidents (false alarms, power outages, maintenance issues)
   • Events related to accidental discharge if it does not involve aircraft or the suppression system causing a fire-related incident
   
   True only if the article describes a valid aviation hangar fire incident or accidental discharge event involving a malfunction of fire suppression systems.

2. **duplicate_index** (integer 0-3):
   Compare the new article with the 3 existing articles:
   • Return 0 if this is a NEW incident
   • Return 1-3 if it matches an existing article (same incident, location, date)
   • Consider articles the same if they describe the same fire event, even with different details

3. **airport_hangar_name** (string):
   • Extract the specific name of the airport, airfield, or hangar facility
   • Include official designations, codes, or proper names
   • Return empty string if not specified

4. **country_region** (string):
   • Extract the country where the incident occurred
   • If country not clear, provide the region/state/province
   • Use standard country names (e.g., "United States", "United Kingdom")

RESPONSE FORMAT:
Return ONLY a valid JSON object with this exact structure:
{{
    "is_valid": boolean,
    "duplicate_index": integer (0-3),
    "airport_hangar_name": "string",
    "country_region": "string"
}}

Be thorough in your analysis and ensure accuracy in classification."""

        return prompt
    
    def _analyze_article(self, existing_articles: List[Dict], new_article: Dict) -> Dict[str, Any]:
        """
        Analyze a new article against existing ones
        """
        prompt = self.create_analysis_prompt(existing_articles, new_article)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            # Parse JSON response
            result = json.loads(result_text)
                
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {result_text}")
            raise
        except Exception as e:
            print(f"API call error: {e}")
            raise
    
    def analyze_article(self, article: Dict) -> Dict[str, Any]:
        """
        Add a new article to the database or storage.
        This method should implement the logic to store the article.
        """
        combined_text = f"""Title: {article.get('title', '')}
Location: {article.get('location', "")}
Description: {article.get('description', "")}
Content: {article.get('content', "")}""".strip()

        similar_articles, query_embedding = get_similar_articles(combined_text, limit=3)

        analysis_result = self._analyze_article(similar_articles, article)
        
        if analysis_result["duplicate_index"] > 0:
            analysis_result["id"] = similar_articles[analysis_result["duplicate_index"] - 1].get("id", None)
        print(f"Analysis result: {analysis_result}")
        
        return analysis_result, query_embedding
