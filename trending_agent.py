"""
TrendingAgent: simple trending logic based on popularity and recency field (if present).
"""
def rank_trending(candidates):
    # Simple ranking: popularity then rating
    return sorted(candidates, key=lambda r: (-r.get("popularity",0), -r.get("rating",0)))
import logging
from datetime import datetime


class TrendingAgent:
    """
    Ranks restaurants by:
        1. Popularity (Zomato-like metric)
        2. Rating
        3. Optional recency boost if 'last_ordered' or 'updated_at' provided

    Works even if DB does NOT have recency fields.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------
    # Parse date safely
    # ------------------------------------------------------
    def _parse_date(self, value):
        """
        Accepts formats:
            "2025-05-01"
            "2025-05-01 10:30"
        Returns datetime or None.
        """
        if not value:
            return None

        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    # ------------------------------------------------------
    # Ranking logic
    # ------------------------------------------------------
    def rank_trending(self, restaurants):
        """
        Returns restaurants sorted by:
            popularity → rating → recent activity (optional)
        """

        ranked_list = []

        for r in restaurants:
            popularity = r.get("popularity", 0)
            rating = r.get("rating", 0)

            # Recency: not required
            last_time = None

            if "last_ordered" in r:
                last_time = self._parse_date(r.get("last_ordered"))

            elif "updated_at" in r:
                last_time = self._parse_date(r.get("updated_at"))

            # Default: very old timestamp
            timestamp = last_time.timestamp() if last_time else 0

            ranked_list.append((popularity, rating, timestamp, r))

        # Sort: popularity ↓, rating ↓, recency ↓
        ranked_list.sort(
            key=lambda item: (-item[0], -item[1], -item[2])
        )

        # Extract only restaurant dicts
        results = [item[3] for item in ranked_list]

        logging.info(f"[TRENDING] Sorted {len(results)} items by popularity, rating & recency.")
        return results
