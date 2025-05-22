# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import json
import webview
from app.utils.config import load_config
from app.utils.translations import load_translations
from app.core import PublicWebViewApi, WebViewApi
from app.utils.utils import check_for_update, get_local_version, unicodefix, ffmpegreg
from app.utils.logs import logs
from app.utils.const import html_file_path
from app.utils.queue import load_queue_from_file

def startApp():
    version = get_local_version()
    update = check_for_update()
    update_js = str(update).lower()

    config = load_config()
    language = config.get("Settings", "language", fallback="en")

    translations = load_translations(language)


    download_queue = load_queue_from_file()

    download_folder = config.get("Settings", "folder_path", fallback="downloads")
    auto_update = config.getboolean("Settings", "auto_update", fallback=False)
    print(config, translations, language)

    print("ЗАПУСК")

    # window = createwindow(html_file_path, api)
    # Создаем окно с HTML-контентом
    real_api = WebViewApi(
        translations = translations,
        language = language,
        download_folder = download_folder,
        download_queue = download_queue,
        update = update_js
    )

    public_api = PublicWebViewApi(real_api)

    window = webview.create_window(
        f'ClipTide {version}',
        html_file_path,
        js_api=public_api, # Передаем API для взаимодействия с JavaScript
        height=780,
        width=1000,
        resizable=True,
        text_select=True
    )
    real_api.set_window(window)

    # api.init_modules(translations, language, update_js, download_folder, download_queue)  # инициализируем модули после
    print("Window created:", window)
        # Загружаем параметры при запуске
    # Перенесите все evaluate_js в обработчик loaded
    def on_loaded():
        window.evaluate_js(f'updateDownloadFolder({json.dumps(download_folder)})')
        window.evaluate_js(f'updateTranslations({json.dumps(translations)})')
        window.evaluate_js(f'window.loadQueue({json.dumps(download_queue)})')
        window.evaluate_js(f'updateApp({update_js}, {json.dumps(translations)})')
        window.evaluate_js(f'setLanguage("{language}")')
        window.evaluate_js('console.log("Window fully loaded!");')
    
    window.events.loaded += on_loaded

    webview.start()

# Основная функция запуска всей программы
def main():
    unicodefix()
    ffmpegreg()
    logs()
    startApp()

if __name__ == "__main__":
    main()