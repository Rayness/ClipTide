# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

from app.modules.downloader import Downloader
from app.modules.converter import Converter
from app.modules.settings import SettingsManager, open_folder
from app.utils.const import THEME_DIR, TRANSLATIONS_DIR
from app.utils.notifications import save_notifications, delete_notification, mark_notification_as_read
from app.utils.themes import get_themes

class PublicWebViewApi:
    def __init__(self, _api):
        self._api = _api

    def openFile(self):
        self._api.converter.openFile()

    def addVideoToQueue(self, videoUrl, selectedFormat, selectedResolution):
        self._api.downloader.addVideoToQueue(videoUrl, selectedFormat, selectedResolution)

    def startDownload(self):
        self._api.downloader.startDownload()

    def removeVideoFromQueue(self, videoTitle):
        self._api.downloader.removeVideoFromQueue(videoTitle)

    def stopDownload(self):
        self._api.downloader.stopDownload()

    def stop_conversion(self):
        self._api.converter.stop_conversion()

    def choose_folder(self):
        self._api.settings.choose_folder()

    def switch_converter_folder(self):
        self._api.settings.switch_converter_folder()

    def switch_download_folder(self):
        self._api.settings.switch_download_folder()

    def choose_converter_folder(self):
        self._api.settings.choose_converter_folder()

    def open_folder(self, folder):
        open_folder(folder)
        print(folder)

    def open_theme_folder(self):
        open_folder(THEME_DIR)
        print(THEME_DIR)

    def open_locale_folder(self):
        open_folder(TRANSLATIONS_DIR)
        print(TRANSLATIONS_DIR)

    def launch_update(self):
        self._api.settings.launch_update()

    def convert_video(self, format):
        self._api.converter.convert_video(format)

    def switch_language(self, lang_code):
        self._api.translations = self._api.settings.switch_language(lang_code)
        self._api.downloader.translations = self._api.translations
        self._api.converter.translations = self._api.translations
    
    def save_notifications(self, notifications):
        save_notifications(notifications)

    def delete_notification(self, id):
        delete_notification(id)

    def minimize(self):
        self._api.window.minimize()

    def toggle_fullscreen(self):
        
        self._api.window.toggle_fullscreen()

    def close(self):
        self._api.window.destroy()

    def mark_notification_as_read(self, id):
        self._api.notifications = mark_notification_as_read(id)
        self._api.downloader.notifications = self._api.notifications
        self._api.converter.notifications = self._api.notifications
        self._api.settings.notifications = self._api.notifications
        print(self._api.notifications)
    
    def saveTheme(self, theme):
        self._api.settings.switch_theme(theme)

    def saveStyle(self, style):
        self._api.settings.switch_style(style)

    def get_themes(self):
        themes = get_themes()
        return themes
    
    def switch_proxy_url(self, proxy):
        self._api.settings.switch_proxy_url(proxy)
        self._api.downloader.proxy_url = proxy

    def switch_proxy(self, proxy):
        self._api.settings.switch_proxy(proxy)
        self._api.downloader.proxy = proxy

    def switch_notifi(self, type, enabled):
        self._api.settings.switch_notifi(type, enabled)
        if type == "downloads":
            self._api.downloader.notification = enabled
        if type == "conversion":
            self._api.converter.notification = enabled

class WebViewApi:
    def __init__(self, translations=None, update=False, language="en", download_folder="", download_queue="", notifications="", theme="", style="", converter_folder="", proxy_url = "", proxy = "False", notifi_download = "True", notifi_conversion = "True"):
        self.window = None
        self.translations = translations
        self.update = update
        self.language = language
        self.download_folder = download_folder
        self.converterFolder = converter_folder
        self.download_queue = download_queue
        self.notifications = notifications
        self.theme = theme
        self.style = style
        self.settings = None
        self.downloader = None
        self.converter = None
        self.proxy_url = proxy_url
        self.proxy = proxy
        self.notifi_download = notifi_download
        self.notifi_conversion = notifi_conversion

    def set_window(self, window):
        self.window = window
        self.settings = SettingsManager(window, self.translations, self.language, self.update, self.download_folder, self.notifications, self.theme, self.converterFolder, self.proxy_url, self.proxy)
        self.downloader = Downloader(window, self.translations, self.download_queue, self.download_folder, self.notifications, self.proxy_url, self.proxy, self.notifi_download)
        self.converter = Converter(window, self.translations, self.converterFolder, self.notifications, self.notifi_conversion)
        print("При инициализации окна: ", self.notifications)


