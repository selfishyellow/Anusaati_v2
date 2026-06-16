from .base import BaseParser
from typing import Optional, Dict, Any
import re

class EnglishParser(BaseParser):
    @property
    def language_code(self) -> str:
        return "en"

    @property
    def invite_keywords(self) -> list[str]:
        return ["enter my room code", "plant a", "join me"]

    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        room_code = self.extract_room_code(text)
        join_url = self.extract_join_url(text)
        
        if not room_code and not join_url:
            return None

        # Pattern: "plant a 180-minute Cuckoo Clock" or "plant a Cuckoo Clock"
        # Often: "plant a {duration}-minute {plant_name}"
        plant_match = re.search(r'plant a (?:(\d+)-minute )?(.+?)(?: with me| to|!|\.|\n|$)', text)
        
        duration = 0
        plant_name = "Unknown"
        
        if plant_match:
            duration_str = plant_match.group(1)
            plant_name = plant_match.group(2).strip()
            if duration_str:
                duration = int(duration_str)
        else:
            # Fallback for duration if not in that specific phrase
            dur_match = re.search(r'(\d+)\s*min', text, re.IGNORECASE)
            if dur_match:
                duration = int(dur_match.group(1))

        return {
            "room_code": room_code,
            "plant_name": plant_name,
            "duration": duration,
            "join_url": join_url
        }
