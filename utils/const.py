import os
from pathlib import Path

appdata_local = os.path.join(os.environ['LOCALAPPDATA'], 'ClipTide')
os.makedirs(appdata_local, exist_ok=True)

download_dir = Path.home() / 'Downloads' / 'ClipTide'
os.makedirs(download_dir, exist_ok=True)

CONFIG_FILE = os.path.join(appdata_local, "config.ini")

QUEUE_FILE = os.path.join(appdata_local, "queue.json")

COOKIES_FILE = os.path.join(appdata_local, "cookies.txt")

UPDATER = "updater.exe"

VERSION_FILE = "./data/version.txt"

GITHUB_REPO = "Rayness/YT-Downloader"

HEADERS = {
    "User-Agent": "Updater-App",
    "Accept": "application/vnd.github.v3+json"
}
# Путь к папке с переводами
TRANSLATIONS_DIR = "./data/localization"

# HTML-контент для отображения в окне
html_file_path = os.path.abspath("data/ui/index.html")