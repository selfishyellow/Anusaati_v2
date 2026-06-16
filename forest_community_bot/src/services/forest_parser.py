from typing import List, Optional, Dict, Any
from src.parsers.base import BaseParser
from src.parsers.english import EnglishParser
from src.parsers.french import FrenchParser
from src.parsers.korean import KoreanParser

class ForestParser:
    def __init__(self):
        self.parsers: List[BaseParser] = [
            EnglishParser(),
            FrenchParser(),
            KoreanParser()
        ]

    def parse_message(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to parse a message with all available parsers.
        Returns the first successful parse result.
        """
        # First pass: check for language-specific keywords
        for parser in self.parsers:
            if any(keyword in text.lower() for keyword in parser.invite_keywords):
                result = parser.parse(text)
                if result and result.get("room_code"):
                    result["language"] = parser.language_code
                    return result
        
        # Second pass: Fallback to join URL if no keywords matched
        for parser in self.parsers:
            if parser.extract_join_url(text):
                result = parser.parse(text)
                if result and result.get("room_code"):
                    result["language"] = parser.language_code
                    return result
        
        return None
