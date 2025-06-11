# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import os
import json
import platform
import subprocess
from tkinter import Tk, filedialog

from app.utils.translations import load_translations

from app.utils.const import download_dir, UPDATER

from app.utils.config import load_config, save_config

config = load_config()

class SettingsManager():
    def __init__(self, window, language, translations, update, notifications, theme, style, folder=None, converterFolder = None, proxy_url = "", proxy = "False"):
        self.window = window
        self.language = language
        self.folder = folder
        self.converterFolder = converterFolder
        self.translations = translations
        self.update = update
        self.theme = theme
        self.style = style
        self.notifications = notifications
        self.proxy_url = proxy_url
        self.proxy = proxy

    # Запуск программы обновления
    def launch_update(self):
        try:
            result = subprocess.run(["powershell", "Start-Process", UPDATER, "-Verb", "runAs"], shell=True)
            print("Код завершения:", result.returncode)
            print("Вывод программы:", result.stdout.decode())
            return result
        except Exception as e:
            print("Ошибки:", result.stderr.decode())
            print(f"Ошибка при запуске апдейтера: {str(e)}")

# Функция для смены языка
    def switch_language(self, language):
        self.language = language
        self.translations = load_translations(language)
        config.set("Settings", "language", self.language)
        save_config(config)
        self.window.evaluate_js(f'updateApp({self.update},{json.dumps(self.translations)})')
        self.window.evaluate_js(f'window.updateTranslations({json.dumps(self.translations)})')
        return self.translations
    
    def switch_theme(self, theme):
        self.theme = theme
        config.set("Themes", "theme", self.theme)
        save_config(config)

    def switch_style(self, style):
        self.style = style
        config.set("Themes", "style", self.style)
        save_config(config)

    def switch_proxy_url(self, proxy):
        self.proxy_url = proxy
        config.set("Proxy", "url", self.proxy_url)
        save_config(config)

    def switch_proxy(self, proxy):
        self.proxy = proxy
        config.set("Proxy", "enabled", self.proxy)
        save_config(config)

    def switch_notifi(self, type, enabled):
        config.set("Notifications", type, enabled)
        save_config(config)

    # Функция для смены папки загрузок
    def switch_download_folder(self, folder_path=f'{download_dir}'):
        self.folder = folder_path if folder_path is not None else download_dir
        config.set("Settings", "folder_path", self.folder)
        save_config(config)
        self.download_folder = self.folder
        print("Folder_path: " + folder_path, "download_folder: " + self.download_folder)
        self.window.evaluate_js(f'updateDownloadFolder({json.dumps(self.folder)})')

    def switch_converter_folder(self, folder_path=f'{download_dir}'):
        self.converterFolder = folder_path if folder_path is not None else download_dir
        config.set("Settings", "converter_folder", self.converterFolder)
        save_config(config)
        print("Converter Folder: " + folder_path)
        self.window.evaluate_js(f'updateConvertFolder({json.dumps(folder_path)})')

    # Функция для выбора папки для загрузки
    def choose_folder(self):
        # Открытие диалогового окна для выбора папки
        root = Tk()
        root.withdraw()  # Скрываем главное окно tkinter
        try:
            folder_path = filedialog.askdirectory()  # Открывает окно выбора папки
            self.window.evaluate_js(f'updateDownloadFolder({json.dumps(folder_path)})')
            self.switch_download_folder(folder_path)
        except Exception as e:
            print(f"Ошибка при выборе папки: {e}")
        root.destroy()

    def choose_converter_folder(self):
        root = Tk()
        root.withdraw()
        try:
            folder_path = filedialog.askdirectory()
            self.switch_converter_folder(folder_path)
        except Exception as e:
            print(f"Ошибка при выборе папка: {e}")
        root.destroy()

# Функция для открытия папки с загрузками
def open_folder(download_folder):
    # try:
    #     if platform.system() == "Windows":
    #         subprocess.run(["explorer", download_folder])
    #     else:
    #         print("Открытие папки не поддерживается на этой ОС.")
    # except Exception as e:
    #     print(f"Ошибка при открытии папки: {e}")
    try:
        os.startfile(f"{download_folder}")
    except Exception as e:
        print(f"Ошибка: {e}")
