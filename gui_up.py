import os
import sys
import threading
import yt_dlp
import webview
import json
import time
import queue
import configparser
import atexit
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

def resource_path(relative_path):
    """ Возвращает корректный путь для доступа к ресурсам после упаковки PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Если приложение запущено в упакованном виде
        base_path = sys._MEIPASS
    else:
        # Если приложение запущено в режиме разработки
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Функция для сохранения очереди перед завершением программы
def on_program_exit():
    if api_instance.download_queue:
        save_queue_to_file(api_instance.download_queue)
        print("Очередь загрузки сохранена перед завершением программы.")

# Регистрация обработчика завершения программы
api_instance = None  # Глобальная переменная для экземпляра Api

# ФАЙЛ КОНФИГУРАЦИИ
# -------------------------------------------------------------------------
CONFIG_FILE = "./config.ini"

QUEUE_FILE = "./queue.json"

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
        except Exception as e:
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
TRANSLATIONS_DIR = resource_path("./gui/localization")

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

def load_queue_from_file():
    """ Загружаем очередь из JSON-файла. """
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def save_queue_to_file(queue):
    """
    Сохраняет очередь загрузки в JSON-файл.
    """
    try:
        with open(QUEUE_FILE, "w", encoding="utf-8") as file:
            json.dump(queue, file, ensure_ascii=False, indent=4)
            print("Очередь загрузки сохранена.")
    except Exception as e:
        print(f"Ошибка при сохранении очереди: {e}")

# --------------------------------------------------------------------------

# HTML-контент для отображения в окне
html_file_path = resource_path("gui/index.html")

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = resource_path(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe")

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = resource_path(str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin"))
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

# Класс для определения API
class Api:
    def __init__(self):
        self.download_queue = load_queue_from_file()
        self.download_folder = ''
        self.is_downloading = False  # Флаг для отслеживания состояния загрузки
    
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
        self.download_folder = self.current_folder
        window.evaluate_js(f'updateDownloadFolder({json.dumps(self.current_folder)})')

    def choose_folder(self):
        # Открытие диалогового окна для выбора папки
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()  # Скрываем главное окно tkinter
        folder_path = filedialog.askdirectory()  # Открывает окно выбора папки
        window.evaluate_js(f'updateDownloadFolder({json.dumps(folder_path)})')
        root.destroy()

    def removeVideoFromQueue(self, video_title):
        try:
            # Фильтруем очередь, удаляя видео с указанным названием
            self.download_queue = [
                (url, title, fmt, res, thumb)
                for url, title, fmt, res, thumb in self.download_queue
                if title != video_title
            ]

            # Сохраняем обновленную очередь в файл
            save_queue_to_file(self.download_queue)

            # Обновляем интерфейс
            window.evaluate_js(f'removeVideoFromList("{video_title}")')

            return f"{translations.get('status', {}).get('removed_from_queue')}: {video_title}"
        except Exception as e:
            return f"{translations.get('status', {}).get('error_removing')}: {str(e)}"

    def addVideoToQueue(self, video_url, selected_format, selectedResolution):
        try:
            # Извлекаем информацию о видео (название)
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'Неизвестное видео')
                thumbnail_url = info.get('thumbnail', '')

            # Добавляем видео в очередь
            self.download_queue.append((video_url, video_title, selected_format, selectedResolution, thumbnail_url))

            # Сохраняем очередь в файл
            save_queue_to_file(self.download_queue)

            # Обновляем интерфейс
            window.evaluate_js(f'addVideoToList("{video_title}", "{thumbnail_url}", "{selected_format}","{selectedResolution}")')
            

            return f"{translations.get('status', {}).get('to_queue')}: {video_title} {translations.get('status', {}).get('in_format')} {selected_format} {translations.get('status', {}).get('in_resolution')} {selectedResolution}p"
        except Exception as e:
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
            os.startfile(f"{download_folder}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('the_queue_is_empty_download_success')}"')
            return

        # Устанавливаем флаг загрузки
        self.is_downloading = True

        save_queue_to_file(self.download_queue)

        # Извлекаем следующее видео из очереди
        video_url, video_title, selected_format, selectedResolution, thumbl = self.download_queue.pop(0)
        window.evaluate_js(f'showSpinner()')

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
                        'preferredcodec': f'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': f'{download_folder}/%(title)s.{selected_format}',  # Путь для сохранения
                    'progress_hooks': [self.progress_hook],  # Добавляем хук для отслеживания прогресса
                    'retries': 25,  # Увеличиваем количество попыток
                    'socket_timeout': 5,  # Устанавливаем таймаут для сокета
                    'nocheckcertificate': True,  # Отключаем проверку SSL-сертификата
                }


            # Загружаем видео
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            self.removeVideoFromQueue(video_title)
            window.evaluate_js(f'hideSpinner()')
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('download_success')}: {video_title}"')
        except Exception as e:
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

if __name__ == "__main__":
    # Создаем экземпляр API
    api = Api()
    api_instance = Api()

    # Создаем окно с HTML-контентом
    window = webview.create_window(
        'YT Downloader',
        html_file_path,
        js_api=api, # Передаем API для взаимодействия с JavaScript
        height=1000,
        resizable=True
    )

    # Загружаем конфигурацию
    config = load_config()

    # Используем настройки
    language = config.get("Settings", "language", fallback="ru")
    download_folder = config.get("Settings", "folder_path", fallback="downloads")
    auto_update = config.getboolean("Settings", "auto_update", fallback=False)

    api.download_folder = download_folder
    download_queue = api.download_queue

    # Загружаем переводы по умолчанию
    translations = load_translations(language)
    window.events.loaded += lambda: window.evaluate_js(f'updateDownloadFolder({json.dumps(download_folder)})')
    window.events.loaded += lambda: window.evaluate_js(f'updateTranslations({json.dumps(translations)})')
    window.events.loaded += lambda: window.evaluate_js(f"window.loadQueue({json.dumps(download_queue)})")

    webview.start()