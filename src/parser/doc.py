import re
from typing import Any, Dict, List
from docx import Document

def split_doc(path: str) -> List[Dict[str, Any]]:
    doc = Document(path)
    content_list = []
    content = ""
    for para in doc.paragraphs:
        # Check if the parameter is a heading
        if para.style.name.startswith('Heading'):
            if content:
                content_list.append(content)
                content = ""
        else:
            content += f"{para.text}\n"
    if content:
        content_list.append(content)
    return content_list

def extract_details(content: str) -> Dict[str, Any]:
    
    patterns = {
        "title": r"Article Title:\s*(.*)",
        "source": r"Publication name:\s*(.*)",
        "location": r"Accident Location:\s*(.*)",
        "publishedAt": r"Article Date:\s*(.*)",
        "author": r"Author:[\t]*(.*)",
        "url": r"Article Link:\s*(\S+)",
        "content": r"Article Link:\s*\S+\s*([\s\S]+)"
    }
    
    details = {}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            details[key] = match.group(1).strip()
        else:
            details[key] = ""

    return details


def doc_parse(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a DOCX file and extract articles.

    Args:
        file_path (str): Path to the DOCX file.

    Returns:
        List[Dict[str, Any]]: List of articles with title and content.
    """
    content_list = split_doc(file_path)
    articles = []
    for content in content_list:
        article = extract_details(content)
        if article["title"]:
           articles.append(article)
    return articles
