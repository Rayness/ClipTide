import os
import subprocess
import sys
sys.path.insert(0, "./libs")
import json
import configparser

config_file = "config.ini"

# Функция для записи данных в INI-файл
def save_config(language, folder_path):
    config = configparser.ConfigParser()

    config.read(config_file)

    config['Settings']['language'] = language
    config['Settings']['folder_path'] = folder_path
    
    with open(config_file, 'w') as file:
        config.write(file)
    print("Конфигурация сохранена.")

# Функция для чтения данных из INI-файла
def load_config():
    config = configparser.ConfigParser()
    config.read(config_file)
    if 'Settings' in config:
        language = config['Settings'].get('language', 'en')  # По умолчанию 'en'
        folder_path = config['Settings'].get('folder_path', 'downloads') # По умолчанию 'downloads'
        return language, folder_path
    else:
        print("Конфигурационный файл не найден или повреждён.")
        return 'en', 'downloads'
    
def load_translations(language):
    with open(f"localization/{language}.json", "r", encoding="utf-8") as file:
        return json.load(file)