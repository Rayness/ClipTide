# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import webview
from pathlib import Path
from modules.core import startApp
from utils.utils import unicodefix, ffmpegreg
from utils.logs import logs

# Основная функция запуска всей программы
def main():
    unicodefix()
    ffmpegreg()
    startApp()
    logs()
    webview.start()

if __name__ == "__main__":
    main()