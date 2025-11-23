import os
import logging

class VisionAgent:
    """
    A lightweight food-detection module.

    - Detects food from image filename
    - Example:  pizza.jpeg  → "pizza"
    - No ML model needed for demo (fast + offline)
    - Can be upgraded later to Groq Vision or CLIP
    """

    def __init__(self):
        # Common Indian + international items
        self.food_keywords = [
            "biryani", "pizza", "burger", "pasta", "momos", "roll",
            "kebab", "chai", "tea", "coffee",
            "icecream", "ice_cream", "ice-cream", "ice cream",
            "kulfi", "lassi", "dosa", "idli", "vada", "uttapam",
            "paneer", "thali", "soup", "paratha",
            "chaat", "pakora", "samosa", "poha", "upma",
            "fries", "sandwich"
        ]

    # -------------------------------------------------------------------
    # Helper: clean filename
    # -------------------------------------------------------------------
    def _clean_filename(self, image_path):
        """Removes directories, extension, special chars."""
        base = os.path.basename(image_path).lower()

        # remove extension
        name = base.split(".")[0]

        # replace separators
        name = name.replace("-", " ").replace("_", " ")

        return name

    # -------------------------------------------------------------------
    # Main Detection
    # -------------------------------------------------------------------
    def detect_food(self, image_path: str):
        """
        Detect food simply by scanning image filename for keywords.
        Example:
            'butter-chicken-roll.png' → 'roll'
        """

        if not image_path or not isinstance(image_path, str):
            logging.info("[VISION] Invalid image path.")
            return None

        cleaned = self._clean_filename(image_path)
        logging.info(f"[VISION] Checking file: {cleaned}")

        # direct match
        for word in self.food_keywords:
            if word in cleaned:
                logging.info(f"[VISION DETECTED] {word}")
                return word

        # split into parts for finer detection
        for part in cleaned.split():
            if part in self.food_keywords:
                logging.info(f"[VISION DETECTED] {part}")
                return part

        logging.info("[VISION] No food detected from filename.")
        return None
