import logging

class AllergyAgent:
    """
    Detects allergies from user text and filters dishes accordingly.

    Examples it can detect:
        - "I am allergic to nuts"
        - "avoid dairy items"
        - "no gluten food"
        - "peanut allergy"
        - "lactose intolerant"
        - "no egg please"
    """

    def __init__(self):
        # Maps allergy keywords → list of unsafe dish ingredients
        self.allergy_map = {
            "nut": ["nut", "peanut", "almond", "cashew", "walnut"],
            "nuts": ["nut", "peanut", "almond", "cashew", "walnut"],
            "peanut": ["peanut", "nut"],
            "dairy": ["milk", "cheese", "curd", "cream", "paneer", "butter", "ghee"],
            "gluten": ["wheat", "bread", "naan", "roti", "pasta", "flour"],
            "lactose": ["milk", "cream", "curd", "cheese", "paneer"],
            "egg": ["egg", "omelette", "egg curry", "scrambled egg"],
            "eggs": ["egg", "omelette", "egg curry"]
        }

    # ------------------------------------------------------
    # DETECT ALLERGIES FROM NATURAL LANGUAGE
    # ------------------------------------------------------
    def detect_allergies(self, text: str):
        """
        Returns a list of allergy keywords detected in the user's message.
        """
        if not text:
            return []

        t = text.lower()
        found = []

        # Exact-match detection
        for key in self.allergy_map:
            if key in t:
                found.append(key)

        # Example: "I'm allergic to peanuts" → detects "peanut"
        if "allergy" in t or "allergic" in t:
            for key in self.allergy_map:
                if key in t:
                    found.append(key)

        # Remove duplicates
        found = list(set(found))

        if found:
            logging.info(f"[ALLERGY DETECTED] {found}")
        return found

    # ------------------------------------------------------
    # REMOVE UNSAFE DISHES BASED ON ALLERGIES
    # ------------------------------------------------------
    def filter_allergies(self, restaurants, user_text):
        """
        Filters out dishes containing unsafe ingredients.

        Input:
            restaurants: List of restaurant dicts
            user_text: User query to detect allergies

        Output:
            Filtered restaurant list with unsafe dishes removed.
        """

        allergies = self.detect_allergies(user_text)

        # No allergy → no filtering
        if not allergies:
            return restaurants

        # Build list of unsafe ingredients across all detected allergies
        unsafe_keywords = []
        for a in allergies:
            unsafe_keywords.extend(self.allergy_map.get(a, []))

        # Ensure no duplicates
        unsafe_keywords = list(set(unsafe_keywords))

        filtered_restaurants = []

        for r in restaurants:
            safe_menu = []

            for dish in r.get("menu_items", []):
                d = dish.lower()

                # If dish contains ANY unsafe ingredient → remove it
                if any(bad in d for bad in unsafe_keywords):
                    continue

                safe_menu.append(dish)

            # Keep restaurant only if it has at least 1 safe dish
            if safe_menu:
                new_r = dict(r)
                new_r["menu_items"] = safe_menu
                filtered_restaurants.append(new_r)

        logging.info(
            f"[ALLERGY FILTER APPLIED] Allergies: {allergies} | "
            f"Remaining Restaurants: {len(filtered_restaurants)}"
        )

        return filtered_restaurants
