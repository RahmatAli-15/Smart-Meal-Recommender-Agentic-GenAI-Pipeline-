class GeneralFoodAgent:
    """
    Handles generic conversation that is NOT a food recommendation query.

    Examples:
        - "Hi"
        - "Hello assistant"
        - "What can you do?"
        - "Who are you?"
        - "Thanks"
        - "How does this work?"
        - "Tell me something"
    """

    def __init__(self):
        pass

    def reply(self, text: str) -> str:
        t = (text or "").lower().strip()

        # -----------------------------------------
        # GREETINGS
        # -----------------------------------------
        if any(w in t for w in ["hi", "hello", "hey", "yo", "hlo"]):
            return "Hi! I can help you find great food, filter by veg/non-veg, fit your budget, or suggest weather-friendly dishes."

        # -----------------------------------------
        # HOW ARE YOU / SMALL TALK
        # -----------------------------------------
        if any(w in t for w in ["how are you", "how r u", "how you doing"]):
            return "I'm doing great! Ready to help you with delicious food suggestions."

        # -----------------------------------------
        # WHO / WHAT ARE YOU
        # -----------------------------------------
        if any(w in t for w in ["who are you", "what are you", "who r u"]):
            return "I'm your personal food assistant — I recommend restaurants, analyze food images, understand weather cravings, and filter based on your preferences."

        # -----------------------------------------
        # CAPABILITY QUESTIONS
        # -----------------------------------------
        if "what can you do" in t or "help" in t or "how does this work" in t:
            return (
                "I can suggest the best dishes near you, filter veg/non-veg, match your budget, "
                "detect allergies, and recommend food based on weather or your cravings."
            )

        # -----------------------------------------
        # THANK YOU
        # -----------------------------------------
        if any(w in t for w in ["thanks", "thank you", "thx", "thanku"]):
            return "You're welcome! Need a food suggestion?"

        # -----------------------------------------
        # COMPLIMENTS
        # -----------------------------------------
        if any(w in t for w in ["good", "awesome", "nice", "smart", "cool"]):
            return "Thanks! Want me to suggest something yummy?"

        # -----------------------------------------
        # GENERIC FOOD TALK
        # -----------------------------------------
        if "food" in t:
            return "Food makes everything better! Tell me what you're craving today."

        # -----------------------------------------
        # DEFAULT FALLBACK
        # -----------------------------------------
        return (
            "I’m here to help you with restaurant suggestions, veg/non-veg options, "
            "budget meals, weather-based food picks, and more. Just ask!"
        )
