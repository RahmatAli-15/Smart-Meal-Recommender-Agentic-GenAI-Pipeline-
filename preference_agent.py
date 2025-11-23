import logging

class PreferenceAgent:
    """
    Detects user taste preferences from natural language:
        - spicy
        - sweet
        - healthy
        - oily
        - light
        - heavy
        - crispy
        - tangy
        - comfort food
        - creamy
        - crunchy

    Returns matching food keywords.
    The FoodRecommenderAgent will use these to filter restaurants.
    """

    def __init__(self):
        # Maps user preference → suggested dish types
        self.pref_map = {
            "spicy": ["biryani", "andhra", "manchurian", "tandoori", "chowmein", "momos"],
            "sweet": ["ice cream", "kulfi", "gulab jamun", "halwa", "brownie", "cake"],
            "healthy": ["salad", "soup", "fruit bowl", "idli", "upma", "grilled"],
            "oily": ["paratha", "bhature", "chole bhature", "pakora", "kebab"],
            "light": ["idli", "soup", "dosa", "sandwich", "salad", "poha"],
            "heavy": ["biryani", "thali", "paneer", "burger", "butter chicken"],
            "crispy": ["pakora", "samosa", "fries", "kachori"],
            "tangy": ["chaat", "pani puri", "bhel puri", "ragda pattice"],
            "comfort": ["khichdi", "dal rice", "paratha", "soup"],
            "creamy": ["butter chicken", "paneer butter masala", "korma"],
            "crunchy": ["fries", "nachos", "pakora"],
        }

        # More natural “synonyms”
        self.synonyms = {
            "spicy": ["spice", "mirchi", "tikha", "hot"],
            "sweet": ["dessert", "meetha"],
            "healthy": ["light food", "diet food"],
            "crispy": ["crunchy", "kurkura"],
            "tangy": ["chatpata"],
            "comfort": ["homely food", "ghar ka khana"],
            "heavy": ["rich food"]
        }

    # -----------------------------------------------------------
    # Expand synonyms → base keyword
    # -----------------------------------------------------------
    def _map_synonym(self, text):
        for base, words in self.synonyms.items():
            for w in words:
                if w in text:
                    return base
        return None

    # -----------------------------------------------------------
    # Detect one or more preferences
    # -----------------------------------------------------------
    def detect_preference(self, text: str):
        t = (text or "").lower()
        found = []

        # Check direct keywords
        for key in self.pref_map:
            if key in t:
                found.append(key)

        # Check synonyms
        syn = self._map_synonym(t)
        if syn:
            found.append(syn)

        # Remove duplicates
        found = list(set(found))

        if found:
            logging.info(f"[PREFERENCE DETECTED] {found}")
        return found

    # -----------------------------------------------------------
    # Return matching dishes
    # -----------------------------------------------------------
    def respond(self, text: str):
        prefs = self.detect_preference(text)
        if not prefs:
            return []

        dishes = []
        for p in prefs:
            dishes.extend(self.pref_map.get(p, []))

        # Remove duplicates
        dishes = list(set(dishes))

        return dishes
