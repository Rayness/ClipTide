import os
import sys
import threading
sys.path.insert(0, "./libs")
import yt_dlp
import webview
import json
import time
import queue
import configparser
from pathlib import Path


# ФАЙЛ КОНФИГУРАЦИИ
# -------------------------------------------------------------------------
CONFIG_FILE = "./gui/config.ini"

# Настройки по умолчанию
DEFAULT_CONFIG = {
    "language": "ru",
    "folder_path": "downloads",
    "auto_update": "False"
}

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        try:
            config.read(CONFIG_FILE, encoding="utf-8")
            print("Конфигурация загружена.")
        except Exception as e:
            print(f"Ошибка при чтении конфигурации: {e}")
            config = create_default_config()
    else:
        print("Файл конфигурации не найден. Создаю новый...")
        config = create_default_config()
    return config

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

# -------------------------------------------------------------------------

# ФАЙЛ С ЛОКАЛИЗАЦИЕЙ
# -------------------------------------------------------------------------

# Путь к папке с переводами
TRANSLATIONS_DIR = "./gui/localization"

def load_translations(language):
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


# --------------------------------------------------------------------------

# HTML-контент для отображения в окне
html_file_path = os.path.abspath("gui/index.html")

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

# Класс для определения API
class Api:
    def __init__(self):
        self.download_queue = []  # Очередь для загрузки видео
        self.is_downloading = False  # Флаг для отслеживания состояния загрузки
        self.download_folder = ''

    def switch_language(self, language):
        self.current_language = language
        translations = load_translations(language)
        config.set("Settings", "language", self.current_language)
        save_config(config)
        window.evaluate_js(f'updateTranslations({json.dumps(translations)})')

    def switch_download_folder(self, folder_path='downloads'):
        self.current_folder = folder_path if folder_path is not None else 'downloads'
        config.set("Settings", "folder_path", self.current_folder)
        save_config(config)
        print(folder_path)
        window.evaluate_js(f'updateDownloadFolder({self.current_folder})')

    def addVideoToQueue(self, video_url, selected_format, selectedResolution, download_folder='downloads'):
        try:
            # Извлекаем информацию о видео (название)
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'Неизвестное видео')

            # Добавляем видео в очередь
            self.download_queue.append((video_url, video_title, selected_format, selectedResolution, download_folder))
            print(f"Видео добавлено в очередь: {video_title} в формате {selected_format} в разрешении {selectedResolution}p")

            # Обновляем интерфейс
            window.evaluate_js(f'addVideoToList("{video_title}")')

            return f"{translations.get('status', {}).get('to_queue')}: {video_title} {translations.get('status', {}).get('in_format')} {selected_format} {translations.get('status', {}).get('in_resolution')} {selectedResolution}p"
        except Exception as e:
            print(f"Ошибка при добавлении видео в очередь: {str(e)}")
            return f"{translations.get('status', {}).get('error_adding')}: {str(e)}"

    def startDownload(self):
        if self.is_downloading:
            return f"{translations.get('status', {}).get('downloading_already')}"

        if not self.download_queue:
            return f"{translations.get('status', {}).get('the_queue_is_empty')}"

        # Запускаем загрузку
        self.start_next_download()
        return f"{translations.get('status', {}).get('download_started')}"

    def start_next_download(self):
        if not self.download_queue:
            os.startfile('downloads')
            print("Очередь пуста. Загрузка завершена.")
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('the_queue_is_empty_download_success')}"')
            return

        # Устанавливаем флаг загрузки
        self.is_downloading = True

        # Извлекаем следующее видео из очереди
        video_url, video_title, selected_format, selectedResolution, download_folder = self.download_queue.pop(0)
        print(f"Начинаю загрузку видео: {video_title} в формате {selected_format} в разрешении {selectedResolution}p")

        # Обновляем статус в интерфейсе
        window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('downloading')}: {video_title}"')
        window.evaluate_js(f'removeVideoFromList("{video_title}")')

        # Запускаем загрузку видео
        threading.Thread(target=self.download_video, args=(video_url, video_title, selected_format, selectedResolution, download_folder)).start()

    def download_video(self, video_url, video_title, selected_format, selectedResolution, download_folder='downloads'):
        try:
            if (selected_format != 'mp3'):
                # Настройки для yt-dlp
                ydl_opts = {
                    'format': f'bestvideo[height<={selectedResolution}]+bestaudio/best[height<={selectedResolution}]',  # Лучшее качество видео и аудио
                    'merge_output_format': selected_format,  # Объединяем видео и аудио в один файл
                    'outtmpl': f'{download_folder}/%(title)s.{selected_format}',  # Путь для сохранения
                    'progress_hooks': [self.progress_hook],  # Добавляем хук для отслеживания прогресса
                    'cookiefile': 'cookies.txt',
                    'retries': 25,  # Увеличиваем количество попыток
                    'socket_timeout': 5,  # Устанавливаем таймаут для сокета
                    'nocheckcertificate': True,  # Отключаем проверку SSL-сертификата
                }
            else:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': f'downloads/%(title)s.{selected_format}',  # Путь для сохранения
                    'progress_hooks': [self.progress_hook],  # Добавляем хук для отслеживания прогресса
                    'retries': 25,  # Увеличиваем количество попыток
                    'socket_timeout': 5,  # Устанавливаем таймаут для сокета
                    'nocheckcertificate': True,  # Отключаем проверку SSL-сертификата
                }


            # Загружаем видео
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            print(f"Видео успешно загружено: {video_title}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('download_success')}: {video_title}"')
        except Exception as e:
            print(f"Ошибка при загрузке: {str(e)}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('download_error')}: {str(e)}')

        # Сбрасываем флаг загрузки и запускаем следующую загрузку
        self.is_downloading = False
        self.start_next_download()

    # Хук для отслеживания прогресса
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Получаем данные о прогрессе
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 1)  # Избегаем деления на ноль
            speed = d.get('speed', 0)  # Скорость в байтах/сек
            eta = d.get('eta', 0)  # Оставшееся время в секундах

            # Вычисляем прогресс
            progress = (downloaded_bytes / total_bytes) * 100 if total_bytes > 0 else 0
            progress = round(progress, 2)  # Округляем до двух знаков после запятой

            # Преобразуем ETA в читаемый формат
            eta_minutes = eta // 60 if eta is not None else 0
            eta_seconds = eta % 60 if eta is not None else 0
            eta_formatted = "Завершение загрузки..." if eta == 0 else f"{int(eta_minutes)} {translations['min']} {int(eta_seconds)} {translations['sec']}"

 # Преобразуем скорость в Мбайты/сек
            speed_mbps = speed / (1024 * 1024) if speed else 0
            speed_formatted = f"{speed_mbps:.2f} {translations['mbs']}"  # Форматируем до двух знаков после запятой

            # Выводим отладочную информацию
            print(f"Progress: {progress}%, Speed: {speed_formatted}, ETA: {eta_formatted}")

            # Обновляем интерфейс
            window.evaluate_js(f'document.getElementById("progress").innerText = "{translations['progress']} {progress}%"')
            window.evaluate_js(f'document.getElementById("speed").innerText = "{translations['speed']} {speed_formatted}"')
            window.evaluate_js(f'document.getElementById("eta").innerText = "{translations['eta']} {eta_formatted}"')

            window.evaluate_js(f'document.getElementById("progress-fill").style.width = "{progress}%"')
        elif d['status'] == 'finished':
            # Загрузка завершена
            window.evaluate_js(f'document.getElementById("progress").innerText = "{translations['progress']} 100%"')
            window.evaluate_js(f'document.getElementById("speed").innerText = "{translations['speed']} 0B/s"')
            window.evaluate_js(f'document.getElementById("eta").innerText = "{translations['eta']} 0 мин 0 сек"')
            window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')


ICON_PATH = "./src/YT-downloader-logo.ico"

if __name__ == "__main__":
    # Создаем экземпляр API
    api = Api()

    # Создаем окно с HTML-контентом
    window = webview.create_window(
        'YT Downloader',
        html_file_path,
        js_api=api,
        height=900,  # Передаем API для взаимодействия с JavaScript
    )
    # Загружаем конфигурацию
    config = load_config()

    # Используем настройки
    language = config.get("Settings", "language", fallback="ru")
    download_folder = config.get("Settings", "folder_path", fallback="downloads")
    auto_update = config.getboolean("Settings", "auto_update", fallback=False)

    print(f"Язык интерфейса: {language}")
    print(f"Папка загрузки: {download_folder}")
    print(f"Автоматическое обновление: {'Включено' if auto_update else 'Выключено'}")

    api.download_folder = download_folder

    # Загружаем переводы по умолчанию
    translations = load_translations(language)
    window.events.loaded += lambda: window.evaluate_js(f'updateDownloadFolder({json.dumps(download_folder)})')
    window.events.loaded += lambda: window.evaluate_js(f'updateTranslations({json.dumps(translations)})')

    print(translations, download_folder)

    webview.start()