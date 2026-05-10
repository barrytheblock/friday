"""
main.py - FRIDAY AI Assistant
Entry point. Connects wake word → STT → Groq → command executor / TTS.
"""

import json
import requests
from groq import Groq

from config         import GROQ_API_KEY, GROQ_MODEL, COMMANDS_URL
from tts_engine     import speak
from stt_engine     import listen_loop
from command_parser import is_command, parse_commands
from command_executor import execute

# ── Groq Client ────────────────────────────────────────────────────────────────

client = Groq(api_key=GROQ_API_KEY)

# ── Commands Reference ─────────────────────────────────────────────────────────

_instructions   = ""
_commands_slim  = ""


def load_commands() -> None:
    """Load commands.json and extract instructions + slim command list."""
    global _instructions, _commands_slim

    raw = None

    if COMMANDS_URL:
        try:
            r   = requests.get(COMMANDS_URL, timeout=10)
            raw = r.json()
            print("[FRIDAY] Commands loaded from remote URL.")
        except Exception as e:
            print(f"[FRIDAY] Remote load failed: {e}. Falling back to local file.")

    if raw is None:
        try:
            with open("commands.json", "r", encoding="utf-8") as f:
                raw = json.load(f)
            print("[FRIDAY] Commands loaded from local file.")
        except FileNotFoundError:
            print("[FRIDAY] Warning: commands.json not found.")
            _instructions  = "You are FRIDAY, a professional AI assistant. Respond helpfully and concisely."
            _commands_slim = "No commands available."
            return

    # Pull instructions from meta block
    _instructions = raw.get("meta", {}).get("instructions", "You are FRIDAY, a professional AI assistant.")

    # Build a slim one-line-per-command list to stay within token limits
    lines = []
    for category, data in raw.get("categories", {}).items():
        for cmd in data.get("commands", []):
            lines.append(f"{cmd['syntax']} — {cmd['description']}")

    _commands_slim = "\n".join(lines)
    print(f"[FRIDAY] {len(lines)} commands loaded ({len(_commands_slim)} chars).")


def build_system_prompt() -> str:
    return f"{_instructions}\n\nAVAILABLE COMMANDS:\n{_commands_slim}"


# ── Groq Inference ─────────────────────────────────────────────────────────────

def ask_friday(user_input: str) -> str:
    """Send user input to Groq and return the response."""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user",   "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq Error] {e}")
        return "I'm having trouble connecting right now."


# ── Response Handler ───────────────────────────────────────────────────────────

def handle_response(ai_response: str) -> None:
    """Execute a command chain or speak a plain text reply."""
    print(f"[AI] {ai_response}")

    if is_command(ai_response):
        commands = parse_commands(ai_response)
        if not commands:
            speak("I understood that as a command, but couldn't parse it.")
            return
        for func_name, args in commands:
            execute(func_name, args)
    else:
        speak(ai_response)


# ── Main ───────────────────────────────────────────────────────────────────────

def on_command(user_text: str) -> None:
    """Called by the listen loop with each recognised command."""
    response = ask_friday(user_text)
    handle_response(response)


def main():
    print("=" * 50)
    print("  F.R.I.D.A.Y. - Online")
    print("=" * 50)

    load_commands()
    speak("FRIDAY online. How can I help?")
    listen_loop(on_command)


if __name__ == "__main__":
    main()
