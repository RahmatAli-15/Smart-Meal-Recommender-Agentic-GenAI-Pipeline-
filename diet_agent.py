import logging

class DietAgent:
    """
    Handles vegetarian / non-vegetarian filtering.

    Smart Veg Mode:
        - Remove ONLY non-veg dishes from restaurants
        - Keep restaurant if at least one veg dish remains
        - If all dishes are non-veg → remove restaurant
    """

    def __init__(self):
        # List of veg keywords (broad coverage)
        self.veg_keywords = [
            "paneer", "veg", "vegetarian", "vegetable", "sabzi", "salad",
            "idli", "dosa", "vada", "dal", "kadhi", "kheer", "poha",
            "upma", "paratha", "roti", "rice", "khichdi", "chole", "bhature",
            "rajma", "khandvi", "dhokla", "thali", "chaat", "kachori",
            "kulfi", "ice cream", "pakora", "samosa", "lassi", "biryani (veg)",
            "aloo", "gobi", "mutter", "corn", "cheese"
        ]

        # Non-veg keywords used to REMOVE dishes only in veg mode
        self.nonveg_keywords = [
            "chicken", "mutton", "fish", "egg", "prawn", "shrimp",
            "beef", "meat", "kebab", "tandoori chicken", "afghani chicken"
        ]

    # ------------------------------------------------------------
    # Detect if a dish should be considered veg
    # ------------------------------------------------------------
    def is_veg_dish(self, dish: str) -> bool:
        """
        Returns True/False based on whether a dish is vegetarian.
        Priority:
            - If any non-veg keyword found → NON-VEG
            - If any veg keyword found → VEG
            - Otherwise assume VEG (to avoid false negative)
        """
        d = dish.lower()

        # Non-veg wins if detected
        if any(word in d for word in self.nonveg_keywords):
            return False

        # Veg if veg keyword found
        if any(word in d for word in self.veg_keywords):
            return True

        # Unknown → assume veg for safety
        return True

    # ------------------------------------------------------------
    # APPLY SMART VEG FILTERING
    # ------------------------------------------------------------
    def smart_filter(self, restaurants: list, diet_mode: str):
        """
        diet_mode: "veg" or "nonveg"
        
        Returns a filtered restaurant list.
        """

        # Non-veg users get full menu
        if diet_mode != "veg":
            return restaurants

        filtered = []

        for r in restaurants:
            menu = r.get("menu_items", [])
            if not menu:
                continue  # skip restaurants with no menu

            # Filter out non-veg dishes
            veg_menu = [item for item in menu if self.is_veg_dish(item)]

            # If no veg options remain → restaurant removed
            if not veg_menu:
                continue

            # Add restaurant with reduced veg-only menu
            new_r = dict(r)
            new_r["menu_items"] = veg_menu
            filtered.append(new_r)

        logging.info(f"[DIET FILTER] Veg mode applied. Restaurants left: {len(filtered)}")
        return filtered
