from .base import BaseParser
from typing import Optional, Dict, Any
import re

class FrenchParser(BaseParser):
    @property
    def language_code(self) -> str:
        return "fr"

    @property
    def invite_keywords(self) -> list[str]:
        return ["code de salle", "planter un"]

    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        room_code = self.extract_room_code(text)
        join_url = self.extract_join_url(text)
        
        if not room_code and not join_url:
            return None

        # Pattern: "planter un {plant_name} de {duration} minutes"
        plant_match = re.search(r'planter un (.+?)(?: de (\d+) minutes)?(?: avec moi| to|!|\.|\n|$)', text, re.IGNORECASE)
        
        duration = 0
        plant_name = "Inconnu"
        
        if plant_match:
            plant_name = plant_match.group(1).strip()
            # If plant_name contains digits and 'minutes', it might have grabbed the duration
            inner_dur = re.search(r'(.+?) de (\d+) minutes', plant_name)
            if inner_dur:
                plant_name = inner_dur.group(1).strip()
                duration = int(inner_dur.group(2))
            else:
                duration_str = plant_match.group(2)
                if duration_str:
                    duration = int(duration_str)
        
        if duration == 0:
            # Fallback for duration
            dur_match = re.search(r'(\d+)\s*min', text, re.IGNORECASE)
            if dur_match:
                duration = int(dur_match.group(1))

        return {
            "room_code": room_code,
            "plant_name": plant_name,
            "duration": duration,
            "join_url": join_url
        }
