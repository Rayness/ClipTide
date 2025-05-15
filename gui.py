# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import os
import webview
import json
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from modules.core import Api, startApp
from utils.config import load_config
from utils.queue import save_queue_to_file
from utils.translations import load_translations
from utils.utils import unicodefix, ffmpegreg, check_for_update
from utils.ui import createwindow
from utils.const import html_file_path

log_dir = Path.home() / 'AppData' / 'Local' / 'ClipTide' / 'Logs'
log_dir.mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

handler = RotatingFileHandler(
    log_dir / 'app.log',
    maxBytes=1024*1024,  # 1 MB
    backupCount=15  # Хранить 5 архивных копий
)
handler.setFormatter(formatter)

logging.basicConfig(handlers=[handler], level=logging.INFO)
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
    webview.start()