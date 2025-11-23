import os
import logging
import requests
import tempfile
import subprocess


class VoiceAgent:
    """
    ElevenLabs + Hinglish voice support
    -----------------------------------
    ✓ Uses ElevenLabs for natural human-like voice
    ✓ Reads API + Voice ID from .env
    ✓ Fallback to SAPI if ElevenLabs missing
    ✓ Zero change needed in main_assistant.py
    """

    def __init__(self, debug=False):
        self.debug = debug

        # Load ElevenLabs credentials
        self.eleven_api_key = os.getenv("ELEVEN_API_KEY")
        self.voice_id = os.getenv("ELEVEN_VOICE_ID")

        # SAPI fallback engine
        self.sapi_engine = None

        # If ElevenLabs missing → fallback
        if not self.eleven_api_key or not self.voice_id:
            logging.warning("[TTS] ElevenLabs key/voice missing → using SAPI fallback")
            self._init_sapi()
        else:
            logging.info("[TTS] ElevenLabs voice enabled")

    # ---------------------------------------------------
    # Optional SAPI Fallback
    # ---------------------------------------------------
    def _init_sapi(self):
        try:
            import pythoncom
            import win32com.client as wincl

            pythoncom.CoInitialize()
            self.sapi_engine = wincl.Dispatch("SAPI.SpVoice")
            logging.info("[SAPI] Fallback voice initialized")

        except Exception as e:
            logging.error(f"[SAPI INIT ERROR] {e}")
            self.sapi_engine = None

    # ---------------------------------------------------
    # Main speak() method
    # ---------------------------------------------------
    def speak(self, text):
        if not text:
            return

        # Try ElevenLabs first
        if self.eleven_api_key and self.voice_id:
            success = self._speak_elevenlabs(text)
            if success:
                return

        # Else fallback to SAPI
        self._speak_sapi(text)

    # ---------------------------------------------------
    # ElevenLabs TTS
    # ---------------------------------------------------
    def _speak_elevenlabs(self, text):
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            headers = {
                "xi-api-key": self.eleven_api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "text": text,
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.75,
                    "style": 0.55,
                    "use_speaker_boost": True
                }
            }

            # Hit ElevenLabs
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                logging.error(f"[ELEVENLABS ERROR] {response.status_code}: {response.text}")
                return False

            # Save temporary MP3
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(response.content)
                mp3_path = tmp.name

            # Play using ffplay (fastest, most reliable, bundled with pip ffmpeg)
            try:
                subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", mp3_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception as e:
                logging.error(f"[FFPLAY ERROR] {e}")
                return False
            finally:
                os.remove(mp3_path)

            return True

        except Exception as e:
            logging.error(f"[ELEVENLABS PLAYBACK ERROR] {e}")
            return False

    # ---------------------------------------------------
    # SAPI fallback
    # ---------------------------------------------------
    def _speak_sapi(self, text):
        try:
            if not self.sapi_engine:
                logging.error("[SAPI ERROR] Engine not initialized")
                return

            import pythoncom
            pythoncom.CoInitialize()

            self.sapi_engine.Speak(text)

        except Exception as e:
            logging.error(f"[SAPI SPEAK ERROR] {e}")
