"""
command_executor.py - Execute FRIDAY commands
Maps parsed command strings to real system actions.
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import datetime
import psutil
import pyautogui
import requests
from pathlib import Path

import tts_engine as tts
from config import APP_PATHS, NOTES_FILE, TODOS_FILE, WEATHER_API_KEY, WEATHER_DEFAULT_CITY

pyautogui.FAILSAFE = False

# ── Timer Storage ──────────────────────────────────────────────────────────────

_active_timers: list[threading.Timer] = []


def _schedule_alert(seconds: float, message: str):
    def _fire():
        tts.speak(message)
    t = threading.Timer(seconds, _fire)
    t.daemon = True
    t.start()
    _active_timers.append(t)


# ── Dispatcher ─────────────────────────────────────────────────────────────────

def execute(func_name: str, args: list):
    """Dispatch a parsed command to its handler function."""
    fn = COMMAND_REGISTRY.get(func_name)
    if fn:
        try:
            fn(*args)
            return True
        except Exception as e:
            print(f"[Executor Error] '{func_name}': {e}")
            tts.speak("I ran into an issue with that command.")
            return False
    else:
        print(f"[Executor] Unknown command: '{func_name}'")
        tts.speak(f"I don't know how to run {func_name} yet.")
        return False


# ── Helpers ────────────────────────────────────────────────────────────────────

def _open_path(path: str):
    """Open a file or folder with its default application."""
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def _launch(executable: str):
    """Launch an app by path, expanding environment variables."""
    exe = os.path.expandvars(str(executable))
    try:
        subprocess.Popen(exe, shell=True)
    except Exception as e:
        print(f"[Launch Error] {e}")
        tts.speak("I couldn't find that application. Please check the path in config.")


def _launch_by_name(name: str):
    """Look up APP_PATHS first, then fall back to shell launch."""
    key = name.lower().strip()
    if key in APP_PATHS:
        _launch(APP_PATHS[key])
    else:
        subprocess.Popen(f'start "" "{name}"', shell=True)


# ── TTS / Flow ─────────────────────────────────────────────────────────────────

def cmd_tts(text: str):          tts.speak(str(text))
def cmd_respond(text: str):      tts.speak(str(text))
def cmd_wait(seconds=1):         time.sleep(float(seconds))
def cmd_run_script(path: str):   subprocess.Popen(["python", str(path)])
def cmd_run_command(cmd: str):   subprocess.Popen(str(cmd), shell=True)

# ── Volume ─────────────────────────────────────────────────────────────────────

def cmd_set_volume(level: int):
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices   = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume    = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(max(0.0, min(1.0, int(level) / 100.0)), None)
    except Exception:
        for _ in range(int(level) // 10):
            pyautogui.press('volumeup')

def cmd_volume_up(amount=10):
    for _ in range(int(amount) // 2):
        pyautogui.press('volumeup')

def cmd_volume_down(amount=10):
    for _ in range(int(amount) // 2):
        pyautogui.press('volumedown')

def cmd_mute():   pyautogui.press('volumemute')
def cmd_unmute(): pyautogui.press('volumemute')

# ── System ─────────────────────────────────────────────────────────────────────

def cmd_screenshot():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    fname   = f"screenshot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
    path    = os.path.join(desktop, fname)
    pyautogui.screenshot().save(path)
    tts.speak(f"Screenshot saved to your desktop.")

def cmd_lock_screen():
    if sys.platform == "win32":
        import ctypes; ctypes.windll.user32.LockWorkStation()

def cmd_sleep_pc():
    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])

def cmd_restart_pc():
    subprocess.run(["shutdown", "/r", "/t", "5"])

def cmd_shutdown_pc():
    subprocess.run(["shutdown", "/s", "/t", "5"])

def cmd_hibernate_pc():
    subprocess.run(["shutdown", "/h"])

def cmd_show_desktop():          pyautogui.hotkey('win', 'd')
def cmd_task_manager():          pyautogui.hotkey('ctrl', 'shift', 'esc')

def cmd_empty_recycle_bin():
    try:
        import winshell
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except Exception as e:
        print(f"[Recycle Bin Error] {e}")

def cmd_set_brightness(level: int):
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(int(level))
    except Exception as e:
        print(f"[Brightness Error] {e}")

def cmd_night_mode_on():
    tts.speak("Please toggle night mode in Windows Settings.")

def cmd_night_mode_off():
    tts.speak("Please toggle night mode in Windows Settings.")

# ── Apps ───────────────────────────────────────────────────────────────────────

def cmd_open_app(name: str):        _launch_by_name(name)
def cmd_close_app(name: str):
    for proc in psutil.process_iter(['name']):
        if name.lower() in proc.info['name'].lower():
            proc.kill()

def cmd_switch_app(name: str):
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(name)
        if windows:
            windows[0].activate()
        else:
            tts.speak(f"No window found for {name}.")
    except Exception as e:
        print(f"[Switch App Error] {e}")

def cmd_open_discord():     _launch_by_name("discord")
def cmd_close_discord():    cmd_close_app("Discord")
def cmd_open_chrome():      _launch_by_name("chrome")
def cmd_open_firefox():     _launch_by_name("firefox")
def cmd_open_edge():        subprocess.Popen(["start", "msedge"], shell=True)
def cmd_open_spotify():     _launch_by_name("spotify")
def cmd_open_vscode():      _launch_by_name("vscode")
def cmd_open_steam():       _launch_by_name("steam")
def cmd_open_minecraft():   _launch_by_name("minecraft")
def cmd_open_notepad():     subprocess.Popen(["notepad.exe"])
def cmd_open_calculator():  subprocess.Popen(["calc.exe"])
def cmd_open_file_explorer(): subprocess.Popen(["explorer.exe"])
def cmd_open_settings():    subprocess.Popen(["start", "ms-settings:"], shell=True)
def cmd_open_obs():         _launch_by_name("obs")
def cmd_open_vlc():         _launch_by_name("vlc")
def cmd_open_word():        subprocess.Popen(["start", "winword"], shell=True)
def cmd_open_excel():       subprocess.Popen(["start", "excel"], shell=True)
def cmd_open_powerpoint():  subprocess.Popen(["start", "powerpnt"], shell=True)
def cmd_open_outlook():     subprocess.Popen(["start", "outlook"], shell=True)
def cmd_open_teams():       _launch_by_name("teams")
def cmd_open_zoom():        _launch_by_name("zoom")
def cmd_open_slack():       _launch_by_name("slack")
def cmd_open_telegram():    _launch_by_name("telegram")
def cmd_open_paint():       subprocess.Popen(["mspaint.exe"])
def cmd_open_snipping_tool(): subprocess.Popen(["snippingtool.exe"])
def cmd_open_terminal():    subprocess.Popen(["wt.exe"])
def cmd_open_powershell():  subprocess.Popen(["powershell.exe"])
def cmd_open_pycharm():     _launch_by_name("pycharm")
def cmd_open_roblox():      _launch_by_name("roblox")
def cmd_open_valorant():    _launch_by_name("valorant")
def cmd_open_epic_games():  _launch_by_name("epic")
def cmd_open_docker():      _launch_by_name("docker")
def cmd_open_postman():     _launch_by_name("postman")

# ── Browser ────────────────────────────────────────────────────────────────────

def cmd_open_url(url: str):           webbrowser.open(url)
def cmd_search_google(query: str):    webbrowser.open(f"https://google.com/search?q={query}")
def cmd_search_youtube(query: str):   webbrowser.open(f"https://youtube.com/results?search_query={query}")
def cmd_search_wikipedia(query: str): webbrowser.open(f"https://en.wikipedia.org/w/index.php?search={query}")
def cmd_search_github(query: str):    webbrowser.open(f"https://github.com/search?q={query}")
def cmd_open_youtube():               webbrowser.open("https://youtube.com")
def cmd_open_github():                webbrowser.open("https://github.com")
def cmd_open_netflix():               webbrowser.open("https://netflix.com")
def cmd_open_twitter():               webbrowser.open("https://twitter.com")
def cmd_open_reddit():                webbrowser.open("https://reddit.com")
def cmd_open_chatgpt():               webbrowser.open("https://chat.openai.com")
def cmd_open_gmail():                 webbrowser.open("https://gmail.com")
def cmd_open_google_maps():           webbrowser.open("https://maps.google.com")
def cmd_navigate_to(location: str):   webbrowser.open(f"https://maps.google.com/maps?q={location}")
def cmd_new_incognito():
    chrome = os.path.expandvars(APP_PATHS.get("chrome", "chrome"))
    subprocess.Popen([chrome, "--incognito"], shell=True)

# ── Files ──────────────────────────────────────────────────────────────────────

def cmd_open_file(path: str):        _open_path(path)
def cmd_open_folder(path: str):      _open_path(path)
def cmd_create_file(path: str):      Path(path).touch()

def cmd_delete_file(path: str):
    try:
        import send2trash
        send2trash.send2trash(path)
    except Exception:
        os.remove(path)

def cmd_copy_file(src: str, dst: str):
    import shutil; shutil.copy2(src, dst)

def cmd_move_file(src: str, dst: str):
    import shutil; shutil.move(src, dst)

def cmd_rename_file(path: str, new_name: str):
    p = Path(path); p.rename(p.parent / new_name)

def cmd_create_folder(path: str):
    os.makedirs(path, exist_ok=True)

def cmd_write_to_file(path: str, content: str):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content + "\n")

def cmd_search_file(name: str):
    webbrowser.open(f"search-ms:query={name}")

# ── Spotify ────────────────────────────────────────────────────────────────────

def cmd_spotify_play():          pyautogui.press('playpause')
def cmd_spotify_pause():         pyautogui.press('playpause')
def cmd_spotify_next():          pyautogui.press('nexttrack')
def cmd_spotify_previous():      pyautogui.press('prevtrack')
def cmd_spotify_volume_up():     pyautogui.hotkey('ctrl', 'up')
def cmd_spotify_volume_down():   pyautogui.hotkey('ctrl', 'down')
def cmd_spotify_like():          pyautogui.hotkey('alt', 'shift', 'b')
def cmd_spotify_shuffle():       pyautogui.hotkey('ctrl', 'shift', 's')
def cmd_spotify_volume(level):   tts.speak("Use set volume for system-level volume control.")
def cmd_spotify_search(q: str):  webbrowser.open(f"https://open.spotify.com/search/{q}")
def cmd_spotify_play_playlist(name: str): webbrowser.open(f"https://open.spotify.com/search/{name}/playlists")
def cmd_spotify_play_artist(name: str):   webbrowser.open(f"https://open.spotify.com/search/{name}/artists")
def cmd_spotify_current_song():  tts.speak("Spotify API connection required. Check config.")

# ── Media Keys ─────────────────────────────────────────────────────────────────

def cmd_media_play_pause():  pyautogui.press('playpause')
def cmd_media_next():        pyautogui.press('nexttrack')
def cmd_media_previous():    pyautogui.press('prevtrack')
def cmd_media_stop():        pyautogui.press('stop')

# ── Discord ────────────────────────────────────────────────────────────────────

def cmd_discord_mute():       pyautogui.hotkey('ctrl', 'shift', 'm')
def cmd_discord_unmute():     pyautogui.hotkey('ctrl', 'shift', 'm')
def cmd_discord_deafen():     pyautogui.hotkey('ctrl', 'shift', 'd')
def cmd_discord_disconnect(): pyautogui.hotkey('ctrl', 'shift', 'd')

# ── Information ────────────────────────────────────────────────────────────────

def cmd_get_time():
    now = datetime.datetime.now()
    tts.speak(f"It is {now.strftime('%I:%M %p')}.")

def cmd_get_date():
    now = datetime.datetime.now()
    tts.speak(f"Today is {now.strftime('%A, %B %d, %Y')}.")

def cmd_get_weather(city: str = ""):
    city = city or WEATHER_DEFAULT_CITY
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": WEATHER_API_KEY, "units": "metric"},
            timeout=5
        )
        d     = r.json()
        desc  = d["weather"][0]["description"]
        temp  = d["main"]["temp"]
        feels = d["main"]["feels_like"]
        tts.speak(f"{city}: {desc}, {temp:.0f} degrees, feels like {feels:.0f}.")
    except Exception:
        tts.speak(f"Couldn't fetch weather for {city}. Check your API key in config.")

def cmd_get_battery():
    b = psutil.sensors_battery()
    if b:
        status = "charging" if b.power_plugged else "on battery"
        tts.speak(f"Battery is at {int(b.percent)} percent, {status}.")
    else:
        tts.speak("No battery sensor detected.")

def cmd_get_ip():
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text
        tts.speak(f"Your public IP is {ip}.")
    except Exception:
        tts.speak("Couldn't retrieve IP address.")

def cmd_calculate(expression: str):
    try:
        result = eval(str(expression), {"__builtins__": {}})
        tts.speak(f"The result is {result}.")
    except Exception:
        tts.speak("I couldn't compute that expression.")

def cmd_get_system_stats():
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    tts.speak(f"CPU at {cpu}%, RAM at {ram}%, disk at {disk}%.")

def cmd_define_word(word: str):
    webbrowser.open(f"https://www.google.com/search?q=define+{word}")

def cmd_get_news():
    webbrowser.open("https://news.google.com")

# ── Productivity ───────────────────────────────────────────────────────────────

def cmd_set_timer(seconds, label="Timer"):
    secs  = float(seconds)
    label = str(label)
    mins  = secs / 60
    display = f"{int(mins)} minute" if mins >= 1 else f"{int(secs)} second"
    tts.speak(f"{display} {label} timer started.")
    _schedule_alert(secs, f"Your {label} timer is done.")

def cmd_set_alarm(time_str: str, label: str = "Alarm"):
    now   = datetime.datetime.now()
    alarm = datetime.datetime.strptime(str(time_str), "%H:%M").replace(
        year=now.year, month=now.month, day=now.day)
    if alarm < now:
        alarm += datetime.timedelta(days=1)
    _schedule_alert((alarm - now).total_seconds(), f"It's {time_str}. {label}.")

def cmd_set_reminder(delay: str, message: str):
    delay   = str(delay)
    message = str(message)
    if delay.endswith('m'):
        secs = float(delay[:-1]) * 60
    elif delay.endswith('h'):
        secs = float(delay[:-1]) * 3600
    elif delay.endswith('s'):
        secs = float(delay[:-1])
    else:
        try:
            now   = datetime.datetime.now()
            alarm = datetime.datetime.strptime(delay, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day)
            secs  = (alarm - now).total_seconds()
        except ValueError:
            tts.speak("I didn't understand that time format.")
            return
    _schedule_alert(secs, f"Reminder: {message}")

def cmd_create_note(content: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(NOTES_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {content}\n")

def cmd_read_notes():
    try:
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            notes = f.read().strip()
        tts.speak(notes if notes else "No notes saved.")
    except FileNotFoundError:
        tts.speak("No notes file found.")

def cmd_add_todo(task: str):
    with open(TODOS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[ ] {task}\n")

def cmd_read_todos():
    try:
        with open(TODOS_FILE, 'r', encoding='utf-8') as f:
            todos = f.read().strip()
        tts.speak(todos if todos else "Your to-do list is empty.")
    except FileNotFoundError:
        tts.speak("No to-do list found.")

def cmd_clear_todos():
    with open(TODOS_FILE, 'w') as f:
        f.write("")

def cmd_start_pomodoro():
    tts.speak("Starting 25 minute focus session.")
    _schedule_alert(25 * 60, "Pomodoro complete. Take a 5 minute break.")

# ── Window Management ──────────────────────────────────────────────────────────

def cmd_minimize_window(): pyautogui.hotkey('win', 'down')
def cmd_maximize_window(): pyautogui.hotkey('win', 'up')
def cmd_close_window():    pyautogui.hotkey('alt', 'f4')
def cmd_snap_left():       pyautogui.hotkey('win', 'left')
def cmd_snap_right():      pyautogui.hotkey('win', 'right')

# ── Typing ─────────────────────────────────────────────────────────────────────

def cmd_type_text(text: str):  pyautogui.write(str(text), interval=0.03)
def cmd_press_key(key: str):   pyautogui.press(str(key))

def cmd_hotkey(keys: str):
    parts = [k.strip() for k in str(keys).split('+')]
    pyautogui.hotkey(*parts)

def cmd_paste_text(text: str):
    import pyperclip
    pyperclip.copy(str(text))
    pyautogui.hotkey('ctrl', 'v')

# ── Command Registry ───────────────────────────────────────────────────────────

COMMAND_REGISTRY = {
    # Flow
    "tts": cmd_tts, "respond": cmd_respond, "wait": cmd_wait,
    "run_script": cmd_run_script, "run_command": cmd_run_command,
    # Volume
    "set_volume": cmd_set_volume, "volume_up": cmd_volume_up,
    "volume_down": cmd_volume_down, "mute": cmd_mute, "unmute": cmd_unmute,
    # System
    "screenshot": cmd_screenshot, "lock_screen": cmd_lock_screen,
    "sleep_pc": cmd_sleep_pc, "restart_pc": cmd_restart_pc,
    "shutdown_pc": cmd_shutdown_pc, "hibernate_pc": cmd_hibernate_pc,
    "show_desktop": cmd_show_desktop, "task_manager": cmd_task_manager,
    "empty_recycle_bin": cmd_empty_recycle_bin,
    "set_brightness": cmd_set_brightness,
    "night_mode_on": cmd_night_mode_on, "night_mode_off": cmd_night_mode_off,
    # Apps
    "open_app": cmd_open_app, "close_app": cmd_close_app, "switch_app": cmd_switch_app,
    "open_discord": cmd_open_discord, "close_discord": cmd_close_discord,
    "open_chrome": cmd_open_chrome, "open_firefox": cmd_open_firefox,
    "open_edge": cmd_open_edge, "open_spotify": cmd_open_spotify,
    "open_vscode": cmd_open_vscode, "open_steam": cmd_open_steam,
    "open_minecraft": cmd_open_minecraft, "open_notepad": cmd_open_notepad,
    "open_calculator": cmd_open_calculator, "open_file_explorer": cmd_open_file_explorer,
    "open_settings": cmd_open_settings, "open_obs": cmd_open_obs,
    "open_vlc": cmd_open_vlc, "open_word": cmd_open_word,
    "open_excel": cmd_open_excel, "open_powerpoint": cmd_open_powerpoint,
    "open_outlook": cmd_open_outlook, "open_teams": cmd_open_teams,
    "open_zoom": cmd_open_zoom, "open_slack": cmd_open_slack,
    "open_telegram": cmd_open_telegram, "open_paint": cmd_open_paint,
    "open_snipping_tool": cmd_open_snipping_tool, "open_terminal": cmd_open_terminal,
    "open_powershell": cmd_open_powershell, "open_pycharm": cmd_open_pycharm,
    "open_roblox": cmd_open_roblox, "open_valorant": cmd_open_valorant,
    "open_epic_games": cmd_open_epic_games, "open_docker": cmd_open_docker,
    "open_postman": cmd_open_postman,
    # Browser
    "open_url": cmd_open_url, "search_google": cmd_search_google,
    "search_youtube": cmd_search_youtube, "search_wikipedia": cmd_search_wikipedia,
    "search_github": cmd_search_github, "open_youtube": cmd_open_youtube,
    "open_github": cmd_open_github, "open_netflix": cmd_open_netflix,
    "open_twitter": cmd_open_twitter, "open_reddit": cmd_open_reddit,
    "open_chatgpt": cmd_open_chatgpt, "open_gmail": cmd_open_gmail,
    "open_google_maps": cmd_open_google_maps, "navigate_to": cmd_navigate_to,
    "new_incognito": cmd_new_incognito,
    # Files
    "open_file": cmd_open_file, "open_folder": cmd_open_folder,
    "create_file": cmd_create_file, "delete_file": cmd_delete_file,
    "copy_file": cmd_copy_file, "move_file": cmd_move_file,
    "rename_file": cmd_rename_file, "create_folder": cmd_create_folder,
    "write_to_file": cmd_write_to_file, "search_file": cmd_search_file,
    # Spotify
    "spotify_play": cmd_spotify_play, "spotify_pause": cmd_spotify_pause,
    "spotify_next": cmd_spotify_next, "spotify_previous": cmd_spotify_previous,
    "spotify_shuffle": cmd_spotify_shuffle, "spotify_volume": cmd_spotify_volume,
    "spotify_volume_up": cmd_spotify_volume_up, "spotify_volume_down": cmd_spotify_volume_down,
    "spotify_like": cmd_spotify_like, "spotify_search": cmd_spotify_search,
    "spotify_play_playlist": cmd_spotify_play_playlist,
    "spotify_play_artist": cmd_spotify_play_artist,
    "spotify_current_song": cmd_spotify_current_song,
    # Media
    "media_play_pause": cmd_media_play_pause, "media_next": cmd_media_next,
    "media_previous": cmd_media_previous, "media_stop": cmd_media_stop,
    # Discord
    "discord_mute": cmd_discord_mute, "discord_unmute": cmd_discord_unmute,
    "discord_deafen": cmd_discord_deafen, "discord_disconnect": cmd_discord_disconnect,
    # Information
    "get_time": cmd_get_time, "get_date": cmd_get_date,
    "get_weather": cmd_get_weather, "get_battery": cmd_get_battery,
    "get_ip": cmd_get_ip, "calculate": cmd_calculate,
    "get_system_stats": cmd_get_system_stats, "define_word": cmd_define_word,
    "get_news": cmd_get_news,
    # Productivity
    "set_timer": cmd_set_timer, "set_alarm": cmd_set_alarm,
    "set_reminder": cmd_set_reminder, "create_note": cmd_create_note,
    "read_notes": cmd_read_notes, "add_todo": cmd_add_todo,
    "read_todos": cmd_read_todos, "clear_todos": cmd_clear_todos,
    "start_pomodoro": cmd_start_pomodoro,
    # Windows
    "minimize_window": cmd_minimize_window, "maximize_window": cmd_maximize_window,
    "close_window": cmd_close_window, "snap_left": cmd_snap_left,
    "snap_right": cmd_snap_right,
    # Typing
    "type_text": cmd_type_text, "press_key": cmd_press_key,
    "hotkey": cmd_hotkey, "paste_text": cmd_paste_text,
}
