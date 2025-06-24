# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import json
import webview
from app.utils.config import load_config
from app.utils.notifications import load_notifications
from app.utils.themes import get_themes
from app.utils.translations import load_translations
from app.core import PublicWebViewApi, WebViewApi
from app.utils.utils import check_for_update, get_local_version, unicodefix, ffmpegreg
from app.utils.logs import logs
from app.utils.const import html_file_path
from app.utils.queue import load_queue_from_file

def startApp():
    version = get_local_version()

    version = str(version).lower()

    update = check_for_update()
    update_js = str(update).lower()
    notifications = load_notifications()
    print(f"Verison: {version}")
    themes = get_themes()

    config = load_config()

    language = config.get("Settings", "language", fallback="en")

    theme = config.get("Themes", "theme", fallback="default")
    style = config.get("Themes", "style", fallback="default")

    notifi_download = config.get("Notifications", "downloads", fallback="True")
    notifi_conversion = config.get("Notifications", "conversion", fallback="True")

    proxy = config.get("Proxy", "url", fallback="")
    proxy_enabled = config.get("Proxy", "enabled", fallback="False")

    translations = load_translations(language)

    download_queue = load_queue_from_file()

    download_folder = config.get("Settings", "folder_path", fallback="downloads")
    converter_folder = config.get("Settings", "converter_folder", fallback="downloads")
    auto_update = config.getboolean("Settings", "auto_update", fallback=False)
    print(config, translations, language)

    print("ЗАПУСК", proxy_enabled, notifi_download)

    real_api = WebViewApi(
        translations = translations,
        language = language,
        download_folder = download_folder,
        download_queue = download_queue,
        update = update_js,
        notifications=notifications,
        theme=theme,
        style=style,
        converter_folder=converter_folder,
        proxy_url=proxy,
        proxy=proxy_enabled,
        notifi_download=notifi_download,
        notifi_conversion=notifi_conversion
    )

    public_api = PublicWebViewApi(real_api)

    window = webview.create_window(
        f'ClipTide {version}',
        html_file_path,
        js_api=public_api,
        height=780,
        width=1200,
        resizable=True,
        text_select=True,
        frameless=True,
    )
    real_api.set_window(window)


    print("Window created:", window)

    def on_loaded():
        window.evaluate_js(f'updateDownloadFolder({json.dumps(download_folder)})')
        window.evaluate_js(f'updateConvertFolder({json.dumps(converter_folder)})')
        window.evaluate_js(f'updateTranslations({json.dumps(translations)})')
        window.evaluate_js(f'window.loadQueue({json.dumps(download_queue)})')
        window.evaluate_js(f'updateApp({update_js}, {json.dumps(translations)})')
        window.evaluate_js(f'setLanguage("{language}")')
        window.evaluate_js(f'loadNotifications({json.dumps(notifications)})')
        window.evaluate_js(f'loadproxy("{proxy}",{json.dumps(proxy_enabled)})')
        window.evaluate_js(f'load_settingsNotificatios("{notifi_download}","{notifi_conversion}")')
        window.evaluate_js(f'loadTheme("{theme}", "{style}", {themes})')
        window.evaluate_js(f'get_version("{version}")')
        
    
    window.events.loaded += on_loaded

    webview.start()

def main():
    unicodefix()
    ffmpegreg()
    logs()
    startApp()

if __name__ == "__main__":
    main()