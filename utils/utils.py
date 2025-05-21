import sys
import os
import subprocess
import requests
from pathlib import Path

from utils.const import GITHUB_REPO, HEADERS, VERSION_FILE

subprocess.CREATE_NO_WINDOW

def unicodefix():
    if sys.platform == "win32":
        try:
            # Способ 1 (Python 3.7+)
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            # Способ 2 (для старых версий Python)
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # 65001 = UTF-8
            # Альтернатива через io
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def resource_path(relative_path):
    """ Возвращает корректный путь для доступа к ресурсам после упаковки PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Если приложение запущено в упакованном виде
        base_path = sys._MEIPASS
    else:
        # Если приложение запущено в режиме разработки
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def ffmpegreg():
    ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
    ffmpeg_exe = resource_path(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe")

    # Добавляем FFmpeg в PATH
    ffmpeg_bin_path = resource_path(str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin"))
    os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

def get_latest_version():
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("tag_name", "0.0.0")
    print(response)
    return "0.0.0"

def get_local_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as file:
            return file.read().strip()
    return "0.0.0"

def check_for_update():
    local = get_local_version()
    latest = get_latest_version()

    if local != latest:
        return True
    else:
        return False
    

def get_appdata_path(app_name: str, roaming: bool = False) -> Path:
    """Возвращает путь к папке приложения в AppData"""
    appdata = os.getenv('APPDATA' if roaming else 'LOCALAPPDATA')
    if not appdata:  # Для Linux/Mac
        appdata = os.path.expanduser('~/.config')
    path = Path(appdata) / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path
