import logging

class WeatherFoodAgent:
    """
    Suggests foods based on weather-related mood words spoken by the user.
    No external API required — pure NLP mood detection.

    Example:
        "It's freezing today" → chai, soup, pakora
        "It's very hot" → ice cream, lassi, cold coffee
        "It's raining" → pakora, samosa, chai
    """

    def __init__(self):

        # Foods ideal for cold weather (warming foods)
        self.cold_map = [
            "chai", "tea", "coffee",
            "soup", "hot chocolate",
            "paratha", "momos", "pakora", "rasam"
        ]

        # Foods ideal for hot weather (cooling foods)
        self.hot_map = [
            "ice cream", "kulfi", "lassi",
            "juice", "shake", "salad",
            "cold coffee"
        ]

        # Foods perfect for rainy weather
        self.rain_map = [
            "pakora", "samosa", "chai",
            "tea", "bhajji", "momos"
        ]

        # Default everyday recommendations
        self.normal_map = [
            "biryani", "pizza", "momos",
            "chaat", "thali", "paratha"
        ]

    # ----------------------------------------------------
    # Detect weather mood from natural language
    # ----------------------------------------------------
    def detect_weather_mood(self, text: str):
        t = (text or "").lower()

        # Cold
        if any(w in t for w in [
            "cold", "freezing", "chilly", "winter", "shivering", "very cold"
        ]):
            return "cold"

        # Hot
        if any(w in t for w in [
            "hot", "heat", "summer", "warm", "very hot", "boiling"
        ]):
            return "hot"

        # Rainy
        if any(w in t for w in [
            "rain", "rainy", "monsoon", "pouring", "drizzling"
        ]):
            return "rain"

        return "normal"

    # ----------------------------------------------------
    # Return a list of weather-based food suggestions
    # ----------------------------------------------------
    def respond(self, text: str):
        mood = self.detect_weather_mood(text)
        logging.info(f"[WEATHER MOOD DETECTED] {mood}")

        if mood == "cold":
            foods = self.cold_map
        elif mood == "hot":
            foods = self.hot_map
        elif mood == "rain":
            foods = self.rain_map
        else:
            foods = self.normal_map

        # Remove duplicates, return consistent ordering
        return sorted(list(set(foods)))
