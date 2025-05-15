# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import os
import webview
from pathlib import Path
from modules.core import startApp
from utils.utils import unicodefix, ffmpegreg
from utils.logs import logs
# ФАЙЛ КОНФИГУРАЦИИ
# -------------------------------------------------------------------------

def get_appdata_path(app_name: str, roaming: bool = False) -> Path:
    """Возвращает путь к папке приложения в AppData"""
    appdata = os.getenv('APPDATA' if roaming else 'LOCALAPPDATA')
    if not appdata:  # Для Linux/Mac
        appdata = os.path.expanduser('~/.config')
    path = Path(appdata) / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path



if __name__ == "__main__":
    unicodefix()
    ffmpegreg()
    startApp()
    logs()
    webview.start()