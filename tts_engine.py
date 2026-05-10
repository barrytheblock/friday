"""
tts_engine.py - FRIDAY Text-to-Speech
Uses Microsoft Edge TTS for a natural female voice.
Falls back to pyttsx3 if edge-tts fails.
"""

import asyncio
import edge_tts
import pygame
import tempfile
import os
import threading
from config import TTS_VOICE, TTS_RATE, TTS_PITCH

pygame.mixer.init()
_tts_lock = threading.Lock()


async def _synthesize(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice=TTS_VOICE, rate=TTS_RATE, pitch=TTS_PITCH)
    await communicate.save(output_path)


def speak(text: str, blocking: bool = True):
    """
    Speak text aloud using the FRIDAY voice.
    blocking=True waits until speech finishes before returning.
    """
    if not text or not text.strip():
        return

    print(f"[FRIDAY] {text}")

    def _speak():
        with _tts_lock:
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    tmp_path = tmp.name

                asyncio.run(_synthesize(text, tmp_path))

                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

            except Exception as e:
                print(f"[TTS Error] {e}")
                _fallback_speak(text)
            finally:
                if tmp_path:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

    if blocking:
        _speak()
    else:
        t = threading.Thread(target=_speak, daemon=True)
        t.start()


def _fallback_speak(text: str):
    """Offline fallback using pyttsx3."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        for voice in engine.getProperty("voices"):
            if "zira" in voice.name.lower() or "female" in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 165)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[Fallback TTS Error] {e}")
