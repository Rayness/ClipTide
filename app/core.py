# core.py

from app.modules.downloader import Downloader
from app.modules.converter import Converter
from app.modules.settings import SettingsManager

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

    def switch_download_folder(self):
        self._api.settings.switch_download_folder()

    def open_folder(self):
        self._api.settings.open_folder()

    def launch_update(self):
        self._api.settings.launch_update()

    def convert_video(self, format):
        self._api.converter.convert_video(format)

    def switch_language(self, lang_code):
        self._api.translations = self._api.settings.switch_language(lang_code)
        self._api.downloader.translations = self._api.translations
        self._api.converter.translations = self._api.translations
    

class WebViewApi:
    def __init__(self, translations=None, update=False, language="en", download_folder="", download_queue=""):
        self.window = None
        self.translations = translations
        self.update = update
        self.language = language
        self.download_folder = download_folder
        self.download_queue = download_queue
        self.settings = None
        self.downloader = None
        self.converter = None

    def set_window(self, window):
        self.window = window
        self.settings = SettingsManager(window, self.translations, self.language, self.update, self.download_folder)
        self.downloader = Downloader(window, self.translations, self.download_queue, self.download_folder)
        self.converter = Converter(window, self.translations, self.download_folder)
