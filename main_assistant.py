# main_assistant.py  (updated)
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Agents
from agents.speech_agent import SpeechAgent
from agents.voice_agent import VoiceAgent
from agents.router_agent import route
from agents.general_food_agent import GeneralFoodAgent
from agents.food_recommender_agent import FoodRecommenderAgent
from agents.weather_food_agent import WeatherFoodAgent
from agents.diet_agent import DietAgent
from agents.budget_agent import BudgetAgent
from agents.allergy_agent import AllergyAgent
from agents.vision_agent import VisionAgent
from agents.teamlead_agent import TeamLeadAgent
from agents.preference_agent import PreferenceAgent
from agents.tastemood_agent import TasteMoodAgent  # mood agent

# Path for persistent user profile
USER_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "data", "user_profile.json")
# Ensure data directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

# -----------------------------
def extract_top1(text: str):
    if not text:
        return ""
    if "\n" in text:
        return text.split("\n")[0]
    return text

def format_results(results, source=None):
    if not results:
        return "No matching restaurants found."

    r = results[0]  # only TOP result

    # Extract menu names from dict-based items
    menu_items = r.get("menu_items", [])
    if isinstance(menu_items, list) and len(menu_items) > 0:
        if isinstance(menu_items[0], dict):
            menu_names = [m.get("name", "") for m in menu_items]
        else:
            menu_names = menu_items
    else:
        menu_names = []

    menu_text = ", ".join(menu_names[:3])

    line = f"{r['name']} — {r['cuisine']} — Rating: {r.get('rating', 0)} — Popular: {menu_text}"

    if source:
        return f"{source}\n{line}"
    return line


# -----------------------------
class MasterAssistant:
    def __init__(self, hybrid_mode=True):
        api_key = os.getenv("GROQ_API_KEY")
        self.hybrid = hybrid_mode

        # Voice + Speech
        self.speech = SpeechAgent(groq_api_key=api_key, debug=False)
        self.voice = VoiceAgent(debug=False)

        # Agents
        self.recommender = FoodRecommenderAgent()
        self.general = GeneralFoodAgent()
        self.weather_food = WeatherFoodAgent()
        self.diet_agent = DietAgent()
        self.budget_agent = BudgetAgent()
        self.allergy = AllergyAgent()
        self.vision = VisionAgent()
        self.teamlead = TeamLeadAgent()
        self.pref_agent = PreferenceAgent()
        self.mood_agent = TasteMoodAgent()

        # User settings
        self.user_diet = None           # "veg" or "nonveg"
        self.user_allergy = None        # list
        self.user_profile = None        # loaded dict (if exists)

        # Load saved profile if exists
        self._load_user_profile()

    # -----------------------------
    def _load_user_profile(self):
        try:
            if os.path.exists(USER_PROFILE_PATH):
                with open(USER_PROFILE_PATH, "r", encoding="utf-8") as f:
                    self.user_profile = json.load(f)
                self.user_diet = self.user_profile.get("diet")
                # normalize
                if self.user_diet:
                    self.user_diet = "veg" if "veg" in self.user_diet.lower() else "nonveg"
                self.user_allergy = self.user_profile.get("allergies", [])
                logging.info(f"[USER PROFILE LOADED] diet={self.user_diet} allergies={self.user_allergy}")
            else:
                logging.info("[USER PROFILE] No saved profile found.")
        except Exception as e:
            logging.exception("Failed to load user profile, continuing without it.")

    # -----------------------------
    def _save_user_profile(self):
        try:
            profile = self.user_profile or {}
            profile["diet"] = self.user_diet
            profile["allergies"] = self.user_allergy or []
            # keep user_id if present
            with open(USER_PROFILE_PATH, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2)
            logging.info(f"[USER PROFILE SAVED] {USER_PROFILE_PATH}")
        except Exception:
            logging.exception("Failed to save user profile.")

    # -----------------------------
    def ask_input(self):
        # Hybrid: try voice first if enabled
        if self.hybrid:
            audio = self.speech.record_audio()
            if audio:
                text = self.speech.audio_to_text(audio)
                if text:
                    logging.info(f"[USER SAID] {text}")
                    return text
        # fallback to text
        text = input("You (text): ").strip()
        logging.info(f"[USER TYPED] {text}")
        return text

    # -----------------------------
    def _ensure_diet(self):
        # If diet already saved, skip asking
        if self.user_diet:
            logging.info("[DIET] already set.")
            return

        # Ask once at startup
        self.voice.speak("Quick question! Are you veg or non-veg?")
        resp = self.ask_input()
        if not resp:
            # default nonveg
            self.user_diet = "nonveg"
            logging.info("[DIET] defaulting to nonveg (no response)")
            return

        t = resp.lower()
        # detect "veg" carefully to avoid "non veg" confusion
        if "non" in t and "veg" in t:
            self.user_diet = "nonveg"
        elif "veg" in t or "vegetarian" in t:
            self.user_diet = "veg"
        else:
            # fallback default
            self.user_diet = "nonveg"

        # persist profile
        if not self.user_profile:
            self.user_profile = {}
        self.user_profile["diet"] = self.user_diet
        self._save_user_profile()

        logging.info(f"[DIET SET] User diet: {self.user_diet}")

    # -----------------------------
    def run(self):
        # startup diet question (only if not saved)
        self._ensure_diet()

       # greet user once
        self.voice.speak("Hello! Ask me a food question or say 'quit' to exit.")

        # SINGLE QUESTION ONLY
        user_input = self.ask_input()

        if not user_input:
            self.voice.speak("I didn't catch that. Please try again later.")
            return

        low = user_input.lower().strip()
        if low in ("exit", "quit", "stop", "goodbye"):
            self.voice.speak("Goodbye! Enjoy your meal.")
            return

        # route
        route_type = route(user_input)
        logging.info(f"[ROUTE SELECTED] {route_type} | Input: {user_input}")

        try:
            # ---------- DIET route ----------
            if route_type == "diet":
                t = user_input.lower()
                if "non" in t and "veg" in t:
                    self.user_diet = "nonveg"
                elif "veg" in t or "vegetarian" in t:
                    self.user_diet = "veg"

                self.user_profile = self.user_profile or {}
                self.user_profile["diet"] = self.user_diet
                self._save_user_profile()
                final = f"Got it! Your preference is {self.user_diet}."

            # ---------- ALLERGY route ----------
            elif route_type == "allergy":
                detected = self.allergy.detect_allergies(user_input)
                self.user_allergy = detected
                self.user_profile = self.user_profile or {}
                self.user_profile["allergies"] = self.user_allergy
                self._save_user_profile()
                final = f"Thanks — I'll avoid: {', '.join(self.user_allergy) if self.user_allergy else 'none'}."

            # ---------- BUDGET route ----------
            elif route_type == "budget":
                price_level = self.budget_agent.extract_budget(user_input)
                results = self.recommender.recommend_by_text(
                    user_input,
                    user_diet=self.user_diet,
                    allergy_list=self.user_allergy,
                    price_level=price_level
                )
                final = format_results(results)

            # ---------- WEATHER FOOD route ----------
            elif route_type == "weather_food":
                foods = self.weather_food.respond(user_input)
                results = self.recommender.recommend_by_text(
                    ", ".join(foods),
                    user_diet=self.user_diet,
                    allergy_list=self.user_allergy
                )
                if results:
                    top = results[0]
                    final = f"{top['name']} — try their {top['menu_items'][0]}."
                else:
                    final = "I couldn't find a good place for this weather."

            # ---------- MOOD route ----------
            elif route_type == "mood":
                foods = self.mood_agent.respond(user_input)
                results = self.recommender.recommend_by_text(
                    ", ".join(foods),
                    user_diet=self.user_diet,
                    allergy_list=self.user_allergy
                )
                final = format_results(results)

            # ---------- VISION route ----------
            elif route_type == "vision":
                self.voice.speak("Please type the full image path now.")
                img_path = input("Image path: ").strip()
                detected = self.vision.detect_food(img_path)
                if not detected:
                    final = "I couldn't detect the food in the image."
                else:
                    results = self.recommender.recommend_by_image(
                        detected,
                        user_diet=self.user_diet,
                        user_loc=None
                    )
                    final = format_results(results, source=f"Detected: {detected}")

            # ---------- RECOMMEND route ----------
            elif route_type == "recommend":
                prefs = self.pref_agent.respond(user_input)
                results = self.recommender.recommend_by_text(
                    user_input,
                    user_diet=self.user_diet,
                    allergy_list=self.user_allergy,
                    price_level=None,
                    preferred_foods=prefs if prefs else None
                )
                final = format_results(results)

            # ---------- GENERAL ----------
            else:
                final = self.general.reply(user_input)

        except Exception:
            logging.exception("Processing error:")
            final = "Something went wrong while processing your request."

        # ---- rewrite + speak answer ----
        top1 = extract_top1(final)
        rewritten = self.teamlead.rewrite(user_input, top1)
        logging.info(f"[RAW TOP1] {top1}")
        logging.info(f"[LLM REWRITE] {rewritten}")

        self.voice.speak(rewritten)

        print("\n------- FULL RESPONSE -------")
        print(final)
        print('Image URL: https://dummyimage.com/600x400/000/fff&text')
        print('Buy Link: https://example.com/buy')
        print("------------------------------\n")

        # SINGLE SHOT END
        self.voice.speak("Goodbye! Enjoy your meal.")
        return
    
    
# -----------------------------
# RUN SINGLE-SHOT ASSISTANT
# -----------------------------
if __name__ == "__main__":
    MasterAssistant(hybrid_mode=True).run()