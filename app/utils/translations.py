# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import os
import json
from app.utils.const import TRANSLATIONS_DIR

def load_translations(language, fallback="ru"):
    file_path = os.path.join(TRANSLATIONS_DIR, f"{language}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                print(file)
                return json.load(file)
        except Exception as e:
            print(f"Ошибка при загрузке переводов: {e}")
    print(f"Файл переводов для языка '{language}' не найден.")
    return {}