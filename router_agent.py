import re

def route(text: str):
    """
    Smart routing for 7-agent Zomato-style AI assistant.
    Supports: English + Hindi + Hinglish.
    """

    if not text:
        return "general"

    t = text.lower().strip()

    # ---------------------------------------------------------
    # 1. STRICT DIET DETECTION (English + Hindi)
    # ---------------------------------------------------------
    if re.search(r"\b(vegetarian|i am veg|pure veg|only veg|शाकाहारी|वेग)\b", t):
        return "diet"

    if re.search(r"\b(non veg|non-veg|i am non veg|i am non vegetarian|मांसाहारी)\b", t):
        return "diet"

    # ---------------------------------------------------------
    # 2. ALLERGY
    # ---------------------------------------------------------
    if any(k in t for k in ["allergy", "allergic", "एलर्जी", "avoid", "reaction"]):
        return "allergy"

    # ---------------------------------------------------------
    # 3. BUDGET
    # ---------------------------------------------------------
    if any(k in t for k in ["cheap", "low cost", "affordable", "कम बजट", "सस्ता"]):
        return "budget"

    if "under" in t:
        return "budget"

    # Numbers + food context
    if re.search(r"\b\d{2,4}\b", t):
        if any(w in t for w in ["food", "eat", "dinner", "lunch", "खाना", "meal"]):
            return "budget"

    # ---------------------------------------------------------
    # 4. WEATHER-BASED FOOD
    # ---------------------------------------------------------
    weather_words = ["cold", "rain", "rainy", "hot", "warm", "गरम", "ठंड", "बारिश"]
    if any(w in t for w in weather_words):
        return "weather_food"

    # ---------------------------------------------------------
    # 5. VISION (Image Upload)
    # ---------------------------------------------------------
    if any(ext in t for ext in [".jpg", ".jpeg", ".png", "image", "photo", "upload", "तस्वीर"]):
        return "vision"

    # ---------------------------------------------------------
    # 6. MOOD-BASED FOOD
    # ---------------------------------------------------------
    mood_words = ["sad", "happy", "bored", "angry", "stress", "stressed", "mood", "मूड"]
    if any(w in t for w in mood_words):
        return "mood"

    # ---------------------------------------------------------
    # 7. RECOMMENDATION (Hindi + Hinglish + English)
    # ---------------------------------------------------------
    recommend_words = [
        "suggest", "recommend", "best", "good place", "restaurant",
        "hungry", "something to eat", "i want food",
        "खाना", "खाना चाहिए", "स्पाइसी", "spicy", "tasty",
        "कुछ", "batao", "बताना", "दिखाओ", "खाने का", "मुझे", "चाहिए"
    ]

    if any(w in t for w in recommend_words):
        return "recommend"

    # ---------------------------------------------------------
    # 8. GENERAL
    # ---------------------------------------------------------
    return "general"
