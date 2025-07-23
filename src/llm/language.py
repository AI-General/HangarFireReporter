import asyncio
import time
from googletrans import Translator

def translate_text(text: str, target_language: str, source_language: str = None) -> str:
    """
    Translate text from source_language to target_language using Google Translate.
    If source_language is None, it will be auto-detected.
    Args:
        text (str): The text to translate.
        target_language (str): The target language code (e.g., 'en', 'fr').
        source_language (str, optional): The source language code. Defaults to None (auto-detect).
    Returns:
        str: The translated text.
    """
    translator = Translator()
    if source_language:
        result = asyncio.run(translator.translate(text, src=source_language, dest=target_language))
    else:
        result = asyncio.run(translator.translate(text, dest=target_language))
    time.sleep(1)
    return result.text


def translate_query(query: str, target_language: str) -> str:
    """
    Split the query by spaces, translate each part to the target language, and combine them.
    Args:
        query (str): The input query string.
        target_language (str): The target language code.
    Returns:
        str: The combined translated string.
    """
    parts = query.split()
    translated_parts = [translate_text(part, target_language) for part in parts]
    return ' '.join(translated_parts)


if __name__ == "__main__":
    # Example 1: Auto-detect source language
    text = "Bonjour tout le monde"
    translated = translate_text(text, target_language="en")
    print(f"Original: {text}")
    print(f"Translated (auto-detect): {translated}")

    # Example 2: Specify source language
    text2 = "Hallo Welt"
    translated2 = translate_text(text2, target_language="fr", source_language="de")
    print(f"Original: {text2}")
    print(f"Translated (de -> fr): {translated2}")

    # Example 3: Chinese to English
    text3 = "你好，世界"
    translated3 = translate_text(text3, target_language="en", source_language="zh-cn")
    print(f"Original: {text3}")
    print(f"Translated (zh-cn -> en): {translated3}")
