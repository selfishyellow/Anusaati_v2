from .base import BaseParser
from typing import Optional, Dict, Any
import re

class KoreanParser(BaseParser):
    @property
    def language_code(self) -> str:
        return "ko"

    @property
    def invite_keywords(self) -> list[str]:
        return ["방 코드", "함께 심으세요", "분 동안", "forestapp.cc"]

    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        room_code = self.extract_room_code(text)
        join_url = self.extract_join_url(text)
        
        if not room_code and not join_url:
            return None

        duration = 0
        plant_name = "알 수 없음"

        # Try to find duration
        dur_match = re.search(r'(\d+)\s*분', text)
        if dur_match:
            duration = int(dur_match.group(1))

        # Try to find plant name
        # "180분 동안 Cuckoo Clock을(를) 심으세요"
        plant_match = re.search(r'분 동안\s+(.+?)(?:을\(를\)|을|를|\s+심으세요|!|\.|\n|$)', text)
        if plant_match:
            plant_name = plant_match.group(1).strip()
        else:
            # Maybe just "Cuckoo Clock을(를) 심으세요"
            plant_match = re.search(r'(.+?)(?:을\(를\)|을|를)\s+심으세요', text)
            if plant_match:
                plant_name = plant_match.group(1).strip()

        return {
            "room_code": room_code,
            "plant_name": plant_name,
            "duration": duration,
            "join_url": join_url
        }
