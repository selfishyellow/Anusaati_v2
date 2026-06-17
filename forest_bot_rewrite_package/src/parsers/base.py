from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import re

class BaseParser(ABC):
    @property
    @abstractmethod
    def language_code(self) -> str:
        pass

    @property
    @abstractmethod
    def invite_keywords(self) -> list[str]:
        pass

    @abstractmethod
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parses the text and returns a dictionary with:
        - room_code
        - plant_name
        - duration (int in minutes)
        - join_url
        """
        pass

    def extract_room_code(self, text: str) -> Optional[str]:
        # Forest room codes are usually 9 characters alphanumeric
        match = re.search(r'\b([A-Z0-9]{9})\b', text)
        return match.group(1) if match else None

    def extract_join_url(self, text: str) -> Optional[str]:
        match = re.search(r'(https://forestapp\.cc/join-room\?token=[A-Z0-9]{9})', text)
        return match.group(1) if match else None
