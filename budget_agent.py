import logging
import re

class BudgetAgent:
    """
    Extracts budget from user text and converts it into a price_level.
    
    Restaurant price_level:
        1 = cheap
        2 = medium
        3 = expensive
    """

    # ------------------------------------------------------
    # EXTRACT BUDGET FROM TEXT
    # ------------------------------------------------------
    def extract_budget(self, text: str):
        """
        Reads rupee amount or keyword from user text.

        Examples:
            "something under 200" → 200 → price_level = 1
            "cheap food" → price_level = 1
            "budget lunch" → price_level = 1
            "mid range" → price_level = 2
            "premium food" → price_level = 3
        """
        if not text:
            return None

        t = text.lower()

        # 1. Extract any numeric budget (e.g., 150, 200, 300)
        nums = re.findall(r"\d+", t)
        if nums:
            rupees = int(nums[0])
            logging.info(f"[BUDGET EXTRACTED] Rupees: {rupees}")
            return self._rupees_to_price_level(rupees)

        # 2. Keyword detection (no numeric budget provided)
        if any(k in t for k in ["cheap", "affordable", "budget", "low"]):
            logging.info("[BUDGET: KEYWORD DETECTED] cheap → price_level=1")
            return 1

        if any(k in t for k in ["mid", "moderate", "medium"]):
            logging.info("[BUDGET: KEYWORD DETECTED] medium → price_level=2")
            return 2

        if any(k in t for k in ["expensive", "premium", "high end"]):
            logging.info("[BUDGET: KEYWORD DETECTED] expensive → price_level=3")
            return 3

        # Nothing detected
        return None

    # ------------------------------------------------------
    # CONVERT RUPEES → PRICE LEVEL
    # ------------------------------------------------------
    def _rupees_to_price_level(self, rupees: int):
        """
        Converts numeric rupee budget to price_level.
        Mapping:
            <= 200  → cheap
            <= 350  → medium
            > 350   → expensive
        """
        if rupees <= 200:
            return 1
        elif rupees <= 350:
            return 2
        else:
            return 3

    # ------------------------------------------------------
    # FILTER RESTAURANTS BY PRICE LEVEL
    # ------------------------------------------------------
    def filter_budget(self, restaurants, price_level):
        """
        Filters restaurants by their price_level.
        
        Keeps only r.price_level <= user's price_level.
        """
        if price_level is None:
            logging.info("[BUDGET FILTER] No filtering applied.")
            return restaurants

        filtered = [
            r for r in restaurants
            if r.get("price_level", 3) <= price_level
        ]

        logging.info(
            f"[BUDGET FILTER APPLIED] Allowed level <= {price_level}. "
            f"Remaining restaurants: {len(filtered)}"
        )

        return filtered
