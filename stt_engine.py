"""
stt_engine.py - Wake word detection and speech recognition
Uses faster-whisper locally — no internet or API key required.
"""

import sounddevice as sd
import wave
import tempfile
import os
from faster_whisper import WhisperModel
from config import WAKE_WORD, WAKE_TIMEOUT, MIC_DEVICE_INDEX

# Load Whisper model once at startup.
# 'base' is recommended — good accuracy, fast enough.
# Options: tiny | base | small | medium (larger = slower but more accurate)
model = WhisperModel("base", device="cpu", compute_type="int8")

SAMPLE_RATE = 16000
DURATION    = 5   # Seconds to record when listening for a command


def _record(seconds: int = DURATION) -> str:
    """Record audio from the microphone and save to a temp .wav file."""
    print(f"[Mic] Recording for {seconds}s...")
    audio = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16',
        device=MIC_DEVICE_INDEX   # None = system default
    )
    sd.wait()

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with wave.open(tmp.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    return tmp.name


def _transcribe(wav_path: str) -> str:
    """Transcribe a .wav file using Whisper. Returns lowercase stripped text."""
    segments, _ = model.transcribe(wav_path, language="en")
    text = " ".join(s.text for s in segments).strip().lower()
    os.unlink(wav_path)
    return text


def _clean(text: str) -> str:
    """Remove punctuation for reliable wake word matching."""
    for ch in [".", ",", "!", "?", "-", ":", ";"]:
        text = text.replace(ch, "")
    return text.strip()


def wait_for_wake_word() -> bool:
    """Continuously listen in 3-second clips until the wake word is heard."""
    print(f"[Listening for wake word: '{WAKE_WORD.upper()}'...]")
    while True:
        wav  = _record(seconds=3)
        text = _transcribe(wav)
        if text:
            clean = _clean(text)
            print(f"[Heard]: {clean}")
            if WAKE_WORD in clean:
                print("[Wake word detected!]")
                return True


def listen_for_command() -> str | None:
    """Record and transcribe a command after the wake word."""
    print("[Listening for command...]")
    wav  = _record(seconds=DURATION)
    text = _transcribe(wav)
    if text:
        print(f"[Command heard]: {text}")
    return text or None


def listen_loop(on_command_callback):
    """
    Main loop: wait for wake word → record command → pass to callback.
    Runs forever until Ctrl+C.
    """
    from tts_engine import speak
    while True:
        try:
            wait_for_wake_word()
            speak("Yes?", blocking=True)   # blocking=True so mic doesn't catch TTS
            command = listen_for_command()
            if command:
                on_command_callback(command)
            else:
                speak("I didn't catch that.")
        except KeyboardInterrupt:
            speak("Shutting down. Goodbye.")
            break
        except Exception as e:
            print(f"[Listen Loop Error] {e}")
            import traceback
            traceback.print_exc()
            continue
