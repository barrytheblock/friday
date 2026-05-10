# ─────────────────────────────────────────────────────────────────
#  FRIDAY - Configuration Template
#  Copy this file to config.py and fill in your values.
#  config.py is listed in .gitignore and will NOT be uploaded.
# ─────────────────────────────────────────────────────────────────

# --- Groq API ---
# Get your free key at: https://console.groq.com
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL   = "llama-3.3-70b-versatile"   # Fast + smart. Alt: "llama-3.1-8b-instant" for max speed

# --- Commands Reference ---
# Upload commands.json to your website and paste the URL here.
# Leave empty "" to use the local commands.json file instead.
COMMANDS_URL = ""

# --- Wake Word ---
WAKE_WORD    = "friday"    # What you say to activate FRIDAY
WAKE_TIMEOUT = 5           # Seconds to listen for a command after activation

# --- TTS Voice ---
# Run `python list_voices.py` to hear all available options
# Recommended female voices:
#   en-GB-SoniaNeural    ← British, calm, professional (default)
#   en-US-AriaNeural     ← American, clear, neutral
#   en-US-JennyNeural    ← American, warm but professional
#   en-AU-NatashaNeural  ← Australian, cool and composed
TTS_VOICE = "en-GB-SoniaNeural"
TTS_RATE  = "-5%"     # Speed: "+10%" faster, "-10%" slower
TTS_PITCH = "-3Hz"    # Pitch: lower = more authoritative

# --- Microphone ---
# Run `python list_devices.py` to find your mic index.
# Set to None to use the system default microphone.
MIC_DEVICE_INDEX = None

# --- Weather ---
# Free API key at: https://openweathermap.org/api
WEATHER_API_KEY      = "your_openweathermap_key_here"
WEATHER_DEFAULT_CITY = "London"   # Used when no city is specified

# --- Notes & Todos Storage ---
import os
NOTES_FILE = os.path.join(os.path.expanduser("~"), "friday_notes.txt")
TODOS_FILE = os.path.join(os.path.expanduser("~"), "friday_todos.txt")

# --- App Paths ---
# Update these to match where apps are installed on your machine.
# Find a path: right-click shortcut → Properties → Target field.
APP_PATHS = {
    "discord":      r"C:\Users\USERNAME\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "minecraft":    r"C:\XboxGames\Minecraft Launcher\Content\Minecraft.exe",
    "steam":        r"C:\Program Files (x86)\Steam\steam.exe",
    "spotify":      r"C:\Users\USERNAME\AppData\Roaming\Spotify\Spotify.exe",
    "vscode":       r"C:\Users\USERNAME\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "obs":          r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    "chrome":       r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":      r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "pycharm":      r"C:\Program Files\JetBrains\PyCharm\bin\pycharm64.exe",
    "roblox":       r"C:\Users\USERNAME\AppData\Local\Roblox\Versions\RobloxPlayerLauncher.exe",
    "valorant":     r"C:\Riot Games\VALORANT\live\VALORANT.exe",
    "epic":         r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
    "vlc":          r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "postman":      r"C:\Users\USERNAME\AppData\Local\Postman\Postman.exe",
    "docker":       r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
    "zoom":         r"C:\Users\USERNAME\AppData\Roaming\Zoom\bin\Zoom.exe",
    "slack":        r"C:\Users\USERNAME\AppData\Local\slack\slack.exe",
    "telegram":     r"C:\Users\USERNAME\AppData\Roaming\Telegram Desktop\Telegram.exe",
}
