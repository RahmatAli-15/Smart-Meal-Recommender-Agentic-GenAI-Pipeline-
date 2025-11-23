import logging

class TasteMoodAgent:
    """
    Maps user mood → suggested food types.
    Used when users say things like:
        - "I'm sad"
        - "I'm bored"
        - "Let's celebrate"
        - "Feeling lazy"
        - "Need comfort food"
        - "I want something exciting"
    """

    def __init__(self):
        # Base mood → dish suggestions
        self.mood_map = {
            "sad": ["khichdi", "dal makhani", "biryani", "warm soup"],
            "down": ["comfort food", "paratha", "dal chawal"],
            "comfort": ["biryani", "dal makhani", "paratha", "soup"],
            "bored": ["chaat", "pani puri", "momos", "spicy noodles"],
            "adventure": ["street food", "momos", "spicy chaat"],
            "excited": ["pizza", "burger", "tandoori"],
            "celebrate": ["desserts", "ice cream", "pizza"],
            "party": ["pizza", "fried chicken", "burgers"],
            "friends": ["fries", "nachos", "pizza"],
            "treat": ["ice cream", "cake", "gulab jamun"],
            "lazy": ["idli", "upma", "sandwich", "khichdi"],
            "stress": ["ice cream", "milkshake", "brownie"],
        }

        # Synonyms/phrases → mood key
        self.mood_synonyms = {
            "sad": ["down", "upset", "bad day"],
            "comfort": ["comforting", "need comfort"],
            "bored": ["nothing to do", "feeling bored"],
            "celebrate": ["party", "promotion", "special day"],
            "lazy": ["tired", "exhausted"],
            "stress": ["tense", "anxious"],
        }

    # ----------------------------------------------------------------
    # Map synonyms → official mood key
    # ----------------------------------------------------------------
    def _normalize_mood(self, text):
        t = text.lower()

        # direct check
        for mood in self.mood_map:
            if mood in t:
                return mood

        # synonym check
        for mood, syns in self.mood_synonyms.items():
            for s in syns:
                if s in t:
                    return mood

        return None

    # ----------------------------------------------------------------
    # Main entry: return list of suggested food items
    # ----------------------------------------------------------------
    def respond(self, text: str):
        mood = self._normalize_mood(text)

        if mood:
            foods = self.mood_map[mood]
            logging.info(f"[MOOD DETECTED] {mood} → {foods}")
            return foods

        # Default fallback mood food
        logging.info("[MOOD] No specific mood detected, using default: biryani")
        return ["biryani"]
