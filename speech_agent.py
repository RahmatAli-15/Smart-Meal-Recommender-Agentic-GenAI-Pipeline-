import os
import logging
import tempfile
import speech_recognition as sr
from groq import Groq


class SpeechAgent:
    """
    Handles:
        - Recording microphone audio
        - Converting raw audio → WAV temp file
        - Sending to Groq Whisper (whisper-large-v3)
        - Returning clean text

    Now optimized for Hinglish (Indian Hindi + English mix).
    """

    def __init__(self, groq_api_key=None, debug=False):
        self.debug = debug
        self.recognizer = sr.Recognizer()

        # Initialize Groq client
        try:
            self.groq = Groq(api_key=groq_api_key)
        except Exception as e:
            logging.error(f"[STT INIT ERROR] Failed to init Groq client: {e}")
            self.groq = None

    # ------------------------------------------------------------
    # Record from microphone
    # ------------------------------------------------------------
    def record_audio(self, timeout=6, phrase_time_limit=6):
        """
        Records microphone audio.
        """
        try:
            with sr.Microphone() as source:
                logging.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                logging.info("Listening...")
                return self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

        except sr.WaitTimeoutError:
            logging.warning("[STT] Timeout: No speech detected.")
            return None

        except Exception as e:
            logging.error(f"[STT RECORD ERROR] {e}")
            return None

    # ------------------------------------------------------------
    # Convert audio → Hinglish text (Hindi + English)
    # ------------------------------------------------------------
    def audio_to_text(self, audio):
        """
        Uploads audio to Groq Whisper.
        Forces Hinglish parsing using `language='hi'`.
        """

        if not audio:
            logging.warning("[STT] No audio received.")
            return None

        if not self.groq:
            logging.error("[STT ERROR] Groq client not initialized.")
            return None

        temp_path = None

        try:
            # Save audio temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio.get_wav_data())
                temp_path = tmp.name

            # STT Hinglish mode
            with open(temp_path, "rb") as f:
                transcript = self.groq.audio.transcriptions.create(
                    file=(temp_path, f.read()),
                    model="whisper-large-v3",
                    response_format="verbose_json",
                    language="hi"       # <---- FORCE HINGLISH / HINDI PARSING
                )

            text = transcript.text.strip()
            logging.info(f"STT OUTPUT (Hinglish): {text}")
            return text

        except Exception as e:
            logging.error(f"[STT FAIL] {e}")
            return None

        finally:
            try:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
