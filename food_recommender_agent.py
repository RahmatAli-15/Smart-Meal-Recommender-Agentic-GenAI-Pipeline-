import json
import os
import logging
from math import radians, cos, sin, asin, sqrt


DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "restaurants.json")


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate distance between two GPS points.
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371 * (2 * asin(sqrt(a)))


class FoodRecommenderAgent:
    """
    Central recommender:
       - Nearby filtering
       - Diet filtering
       - Allergy filtering
       - Keyword filtering
       - Mood/weather preference support
       - Budget-level filtering
       - Trending / popularity sorting
    """

    def __init__(self, data_path=DATA_PATH):
        with open(data_path, "r", encoding="utf-8") as f:
            self.restaurants = json.load(f)

    # ---------------------------------------------------------
    # Nearby logic
    # ---------------------------------------------------------
    def _nearby(self, lat, lon, radius_km=5.0):
        if lat is None or lon is None:
            return sorted(
                self.restaurants,
                key=lambda r: (-r["rating"], -r["popularity"])
            )

        out = []
        for r in self.restaurants:
            try:
                d = haversine(lon, lat, r["longitude"], r["latitude"])
            except:
                d = 9999

            if d <= radius_km:
                out.append((d, r))

        out.sort(key=lambda x: (x[0], -x[1]["rating"]))
        return [r for _, r in out]

    # ---------------------------------------------------------
    # Diet filter
    # ---------------------------------------------------------
    def filter_diet(self, restaurants, user_diet):
        if not user_diet:
            return restaurants

        if user_diet == "nonveg":
            return restaurants  # no filtering required

        filtered = []
        for r in restaurants:
            veg_items = [
                item for item in r["menu_items"]
                if not any(meat in item.lower() for meat in
                           ["chicken", "mutton", "fish", "beef", "egg", "prawn"])
            ]
            if veg_items:
                new_r = r.copy()
                new_r["menu_items"] = veg_items
                filtered.append(new_r)

        logging.info(f"[DIET FILTER] Veg mode → {len(filtered)} restaurants left.")
        return filtered

    # ---------------------------------------------------------
    # Allergy filter
    # ---------------------------------------------------------
    def filter_allergy(self, restaurants, allergy_list):
        if not allergy_list:
            return restaurants

        filtered = []
        for r in restaurants:
            safe_dishes = []
            for dish in r["menu_items"]:
                d = dish.lower()
                if any(a in d for a in allergy_list):
                    continue
                safe_dishes.append(dish)

            if safe_dishes:
                new_r = r.copy()
                new_r["menu_items"] = safe_dishes
                filtered.append(new_r)

        logging.info(f"[ALLERGY FILTER] Applied {allergy_list}. Remaining: {len(filtered)}")
        return filtered

    # ---------------------------------------------------------
    # Budget filter
    # ---------------------------------------------------------
    def filter_budget(self, restaurants, price_level):
        if not price_level:
            return restaurants

        filtered = [
            r for r in restaurants
            if r.get("price_level", 3) <= price_level
        ]

        logging.info(f"[BUDGET FILTER] price_level <= {price_level} → {len(filtered)} left.")
        return filtered

    # ---------------------------------------------------------
    # Keyword based filtering
    # ---------------------------------------------------------
    def keyword_filter(self, restaurants, text):
        t = (text or "").lower()

        # Italian
        if "pizza" in t:
            restaurants = [r for r in restaurants if "italian" in r["cuisine"].lower()]

        # Chai
        if "chai" in t or "tea" in t:
            restaurants = [r for r in restaurants if
                           "chai" in " ".join(r["menu_items"]).lower()]

        return restaurants

    # ---------------------------------------------------------
    # Main recommendation function
    # ---------------------------------------------------------
    def recommend_by_text(
        self,
        text,
        user_loc=None,
        user_diet=None,
        allergy_list=None,
        price_level=None,
        preferred_foods=None
    ):
        """
        preferred_foods = list of food items returned by:
           - TasteMoodAgent
           - WeatherFoodAgent
           - PreferenceAgent
        """

        t = text.lower()

        # Location
        lat, lon = (None, None)
        if user_loc:
            lat, lon = user_loc

        # Step 1 — Nearby
        results = self._nearby(lat, lon)

        # Step 2 — Preferred foods from mood/weather
        if preferred_foods:
            pf = [p.lower() for p in preferred_foods]
            results = [
                r for r in results
                if any(p in " ".join(r["menu_items"]).lower() for p in pf)
            ]

        # Step 3 — Keyword filtering
        results = self.keyword_filter(results, t)

        # Step 4 — Diet
        results = self.filter_diet(results, user_diet)

        # Step 5 — Allergy
        results = self.filter_allergy(results, allergy_list)

        # Step 6 — Budget
        results = self.filter_budget(results, price_level)

        # Final sort
        results = sorted(
            results,
            key=lambda r: (-r["rating"], -r["popularity"])
        )

        return results[:10]

    # ---------------------------------------------------------
    # Weather-based recommendation helper
    # ---------------------------------------------------------
    def recommend_for_weather(self, foods, user_loc=None, user_diet=None):
        text = ", ".join(foods)
        return self.recommend_by_text(text, user_loc, user_diet)

    # ---------------------------------------------------------
    # Vision → dish name → text-based recommender
    # ---------------------------------------------------------
    def recommend_by_image(self, dish_name, user_loc=None, user_diet=None):
        return self.recommend_by_text(dish_name, user_loc, user_diet)
