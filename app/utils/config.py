# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import os
import configparser
from app.utils.const import download_dir, CONFIG_FILE

# Настройки по умолчанию
DEFAULT_CONFIG = {
    "language": "ru",
    "folder_path": f"{download_dir}",
    "auto_update": "False"
}

def load_config():
    config = configparser.ConfigParser()
    
    # Создаем дефолтную конфигурацию, если файла нет
    if not os.path.exists(CONFIG_FILE):
        print("Файл конфигурации не найден. Создаю новый...")
        return create_default_config()
    
    try:
        # Читаем файл с явным указанием кодировки
        with open(CONFIG_FILE, 'r', encoding='utf-8') as configfile:
            config.read_file(configfile)
        return config
    except UnicodeDecodeError:
        # Пробуем альтернативную кодировку, если utf-8 не сработала
        try:
            with open(CONFIG_FILE, 'r', encoding='cp1251') as configfile:
                config.read_file(configfile)
            print("")
            return config
        except Exception as e:
            print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Если все попытки чтения провалились, создаем дефолтную конфиг
    return create_default_config()

def create_default_config():
    config = configparser.ConfigParser()
    config["Settings"] = DEFAULT_CONFIG
    save_config(config)
    return config

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            config.write(file)
            print("Конфигурация сохранена.")
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации: {e}")

