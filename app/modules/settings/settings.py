# app/modules/settings/settings.py

import json
import subprocess
import platform
# from tkinter import Tk, filedialog
from app.utils.const import download_dir, UPDATER
from app.utils.locale.translations import load_translations

# Эту функцию можно оставить здесь или вынести в utils.py
def open_folder(folder_path):
    try:
        if platform.system() == "Windows":
            subprocess.run(["explorer", folder_path])
        else:
            subprocess.run(['xdg-open', folder_path])
    except Exception as e:
        print(f"Ошибка при открытии папки: {e}")

class SettingsManager:
    def __init__(self, context):
        self.ctx = context # Вся сила теперь здесь

    def launch_update(self):
        try:
            subprocess.run(["powershell", "Start-Process", UPDATER, "-Verb", "runAs"], shell=True)
        except Exception as e:
            print(f"Ошибка при запуске апдейтера: {str(e)}")

    def switch_language(self, language):
        self.ctx.language = language
        self.ctx.translations = load_translations(language)
        self.ctx.update_config_value("Settings", "language", language)
        
        # Обновляем UI
        # Предполагаем, что updateApp и updateTranslations делают одно и то же, упрощаем:
        self.ctx.js_exec(f'window.updateTranslations({json.dumps(self.ctx.translations)})')
        self.ctx.js_exec(f'setLanguage("{language}")')
        return self.ctx.translations

    def switch_theme(self, theme):
        self.ctx.theme = theme
        self.ctx.update_config_value("Themes", "theme", theme)

    def switch_style(self, style):
        self.ctx.style = style
        self.ctx.update_config_value("Themes", "style", style)

    def switch_proxy_url(self, proxy):
        self.ctx.proxy_url = proxy
        self.ctx.update_config_value("Proxy", "url", proxy)

    def switch_proxy(self, enabled):
        self.ctx.proxy_enabled = enabled
        self.ctx.update_config_value("Proxy", "enabled", enabled)

    def switch_notifi(self, n_type, enabled):
        self.ctx.update_config_value("Notifications", n_type, enabled)

    def switch_open_folder_dl(self, f_type, enabled):
        self.ctx.update_config_value("Folders", f_type, enabled)

    def switch_download_folder(self, folder_path=None):
        path = folder_path if folder_path else download_dir
        self.ctx.download_folder = path
        self.ctx.update_config_value("Settings", "folder_path", path)
        self.ctx.js_exec(f'updateDownloadFolder({json.dumps(path)})')

    def switch_converter_folder(self, folder_path=None):
        path = folder_path if folder_path else download_dir
        self.ctx.converter_folder = path
        self.ctx.update_config_value("Settings", "converter_folder", path)
        self.ctx.js_exec(f'updateConvertFolder({json.dumps(path)})')

    def choose_folder(self):
        import webview
        folder_path = self.ctx.window.create_file_dialog(
            webview.FOLDER_DIALOG,
            allow_multiple=False
        )
        
        # Метод возвращает кортеж или None
        if folder_path and len(folder_path) > 0:
            path = folder_path[0] # Берем первый путь
            self.switch_download_folder(path)

    def choose_converter_folder(self):
        import webview
        folder_path = self.ctx.window.create_file_dialog(
            webview.FOLDER_DIALOG,
            allow_multiple=False
        )
        
        if folder_path and len(folder_path) > 0:
            path = folder_path[0]
            self.switch_converter_folder(path)

    # def _open_dialog(self):
    #     root = Tk()
    #     root.withdraw()
    #     path = filedialog.askdirectory()
    #     root.destroy()
    #     return path