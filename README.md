# F.R.I.D.A.Y.

A locally-running AI voice assistant powered by Groq and Whisper.
Wake-word activated, female British voice, 130+ system commands.

---

## Features

- Wake word detection — say **"Friday"** to activate
- Local speech recognition via **faster-whisper** (no internet required for STT)
- AI responses via **Groq** (fast, free tier available)
- Natural female British TTS voice via **edge-tts**
- 130+ commands: apps, browser, Spotify, Discord, files, timers, system control, and more
- Command chaining — e.g. *"open Chrome then go to YouTube"*
- Separate microphone support — won't conflict with Discord

---

## Project Structure

```
friday/
├── main.py               ← Entry point — run this
├── config.example.py     ← Copy to config.py and fill in your keys
├── tts_engine.py         ← Text-to-speech (edge-tts)
├── stt_engine.py         ← Wake word + speech recognition (faster-whisper)
├── command_parser.py     ← Parses -command() then command() strings
├── command_executor.py   ← Maps commands to real system actions
├── commands.json         ← Full command reference (AI reads this)
├── list_devices.py       ← Helper: find your microphone index
└── requirements.txt      ← Python dependencies
```

> **Note:** `config.py` is in `.gitignore` and is never uploaded. It contains your API keys.

---

## Setup

### 1. Clone and enter the folder
```bash
git clone https://github.com/yourusername/friday.git
cd friday
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> **PyAudio / sounddevice on Windows:** If sounddevice fails, run `pip install pipwin && pipwin install pyaudio`

### 3. Create your config
```bash
copy config.example.py config.py
```
Then open `config.py` and fill in:
- `GROQ_API_KEY` → free at https://console.groq.com
- `WEATHER_API_KEY` → free at https://openweathermap.org/api
- `APP_PATHS` → update paths to match your installed apps

### 4. (Optional) Find your microphone index
```bash
python list_devices.py
```
Set `MIC_DEVICE_INDEX` in `config.py` if you want to use a specific mic.

### 5. Run
```bash
python main.py
```

---

## Usage

Say **"Friday"** → wait for *"Yes?"* → give your command.

### Example Commands

| Say                                  | FRIDAY does                          |
|--------------------------------------|--------------------------------------|
| *"Open Discord"*                     | Launches Discord                     |
| *"Play AC/DC on Spotify"*            | Opens Spotify search for AC/DC       |
| *"Set volume to 40"*                 | Sets system volume to 40%            |
| *"Take a screenshot"*                | Saves screenshot to Desktop          |
| *"Open Chrome and go to YouTube"*    | Opens Chrome → navigates to YouTube  |
| *"Set a 10 minute timer"*            | Starts timer, speaks when done       |
| *"What time is it?"*                 | Speaks the current time              |
| *"Mute Discord"*                     | Mutes Discord mic                    |
| *"Create a note: buy coffee"*        | Saves note to your notes file        |
| *"Shutdown the computer"*            | Shuts down in 5 seconds              |

---

## How the Command System Works

FRIDAY's AI returns one of two things:

**A command string** (starts with `-`):
```
-open_chrome() then tts("Chrome is ready.")
```

**Plain text** (a conversational reply):
```
Alexander Graham Bell invented the telephone in 1876.
```

Commands are parsed and each function is executed in sequence.
The `then` keyword chains them with optional `wait()` steps between.

---

## Adding Custom Commands

1. Add an entry to `commands.json` under the appropriate category
2. Add the handler function in `command_executor.py`
3. Register it in `COMMAND_REGISTRY` at the bottom of `command_executor.py`

---

## Voices

Change `TTS_VOICE` in `config.py`:

| Voice | Style |
|---|---|
| `en-GB-SoniaNeural` | British, calm, professional (default) |
| `en-US-AriaNeural` | American, clear, neutral |
| `en-US-JennyNeural` | American, warm |
| `en-AU-NatashaNeural` | Australian, composed |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Mic not detected | Run `python list_devices.py`, set `MIC_DEVICE_INDEX` in config |
| Wake word ignored | Try speaking slower, or change `WAKE_WORD` to something easier |
| App not opening | Update the path in `APP_PATHS` in `config.py` |
| TTS not working | Check internet connection (edge-tts needs it) |
| Groq quota error | Switch `GROQ_MODEL` to `"llama-3.1-8b-instant"` |

---

## License

MIT — do whatever you want with it.
