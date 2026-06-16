import os
from rapidfuzz import process, utils
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AssetManager:
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self.plants: Dict[str, str] = {} # Normalized name -> Filename
        self.load_assets()

    def load_assets(self):
        """Scans the assets directory and populates the plants dictionary."""
        if not os.path.exists(self.assets_dir):
            logger.warning(f"Assets directory {self.assets_dir} not found.")
            return

        for filename in os.listdir(self.assets_dir):
            if filename.endswith(".png"):
                # Normalize filename: remove extension, replace underscores/hyphens with spaces, lowercase
                name = os.path.splitext(filename)[0]
                normalized_name = name.replace("_", " ").replace("-", " ").lower()
                self.plants[normalized_name] = filename
        
        logger.info(f"Loaded {len(self.plants)} plant assets.")

    def get_plant_image(self, query: str) -> Tuple[Optional[str], float]:
        """
        Fuzzy matches the query against loaded plant names.
        Returns a tuple of (filename, score).
        """
        if not self.plants:
            return None, 0.0

        normalized_query = query.lower()
        choices = list(self.plants.keys())
        
        result = process.extractOne(normalized_query, choices, processor=utils.default_process)
        
        if result:
            matched_name, score, index = result
            if score > 60: # Threshold for a decent match
                return self.plants[matched_name], score
        
        return None, 0.0

    def get_asset_path(self, filename: str) -> str:
        return os.path.join(self.assets_dir, filename)
