import logging
from groq import Groq
import os


class TeamLeadAgent:
    """
    Rewrites restaurant responses into short,
    friendly Zomato-style Hinglish ordering suggestions.
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logging.error("GROQ_API_KEY is missing!")

        try:
            self.client = Groq(api_key=api_key)
        except Exception as e:
            logging.error(f"[TEAMLEAD INIT ERROR] {e}")
            self.client = None

    # ---------------------------------------------------------
    # HINGLISH ORDERING REWRITE
    # ---------------------------------------------------------
    def rewrite(self, user_query: str, raw_top1: str) -> str:
        """
        Creates a friendly Hinglish response that tells the user
        to ORDER from the restaurant on Zomato.
        """

        if not self.client:
            logging.error("[TEAMLEAD] Client unavailable → using fallback.")
            return raw_top1

        prompt = f"""
Rewrite the restaurant recommendation into a short, friendly Hinglish message,
but ALWAYS frame it as an online food ORDER on Zomato — NOT visiting the place.

User asked: {user_query}
Recommendation: {raw_top1}

Rules:
- Hinglish tone (Hindi + English mix)
- 2 short sentences max
- Keep restaurant name SAME
- Keep dish names SAME
- Do NOT tell user to "go" or "visit" restaurant
- MUST say something like "order karlo", "Zomato se mangwa lo", "delivery karwa lo"
- No emojis
- Keep it casual, fun, very Indian
"""

        try:
            resp = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            reply = resp.choices[0].message.content.strip()
            logging.info(f"[TEAMLEAD REWRITE] {reply}")
            return reply

        except Exception as e:
            logging.error(f"[TEAMLEAD ERROR] {e}")
            return raw_top1
