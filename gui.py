# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import os
import sys
import subprocess
import threading
import yt_dlp
import webview
import json
import configparser
from configparser import ConfigParser
import requests
from tkinter import Tk, filedialog
from pathlib import Path
import re
import time
import ffmpeg
import io
import re
import logging
from threading import Thread
from logging.handlers import RotatingFileHandler

subprocess.CREATE_NO_WINDOW

if sys.platform == "win32":
    try:
        # Способ 1 (Python 3.7+)
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Способ 2 (для старых версий Python)
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # 65001 = UTF-8
        # Альтернатива через io
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        
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

log_dir = Path.home() / 'AppData' / 'Local' / 'ClipTide' / 'Logs'
log_dir.mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

handler = RotatingFileHandler(
    log_dir / 'app.log',
    maxBytes=1024*1024,  # 1 MB
    backupCount=15  # Хранить 5 архивных копий
)
handler.setFormatter(formatter)

logging.basicConfig(handlers=[handler], level=logging.INFO)
# ФАЙЛ КОНФИГУРАЦИИ
# -------------------------------------------------------------------------
appdata_local = os.path.join(os.environ['LOCALAPPDATA'], 'ClipTide')
os.makedirs(appdata_local, exist_ok=True)

download_dir = Path.home() / 'Downloads' / 'ClipTide'
os.makedirs(download_dir, exist_ok=True)

CONFIG_FILE = os.path.join(appdata_local, "config.ini")

QUEUE_FILE = os.path.join(appdata_local, "queue.json")

COOKIES_FILE = os.path.join(appdata_local, "cookies.txt")

UPDATER = "updater.exe"

VERSION_FILE = "./data/version.txt"

GITHUB_REPO = "Rayness/YT-Downloader"

HEADERS = {
    "User-Agent": "Updater-App",
    "Accept": "application/vnd.github.v3+json"
}

def get_appdata_path(app_name: str, roaming: bool = False) -> Path:
    """Возвращает путь к папке приложения в AppData"""
    appdata = os.getenv('APPDATA' if roaming else 'LOCALAPPDATA')
    if not appdata:  # Для Linux/Mac
        appdata = os.path.expanduser('~/.config')
    path = Path(appdata) / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_latest_version():
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("tag_name", "0.0.0")
    print(response)
    return "0.0.0"

def get_local_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as file:
            return file.read().strip()
    return "0.0.0"

def check_for_update():
    local = get_local_version()
    latest = get_latest_version()

    if local != latest:
        return True
    else:
        return False

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
        window.evaluate_js(f'ERROR: {e}')


# -------------------------------------------------------------------------

# ФАЙЛ С ЛОКАЛИЗАЦИЕЙ
# -------------------------------------------------------------------------

# Путь к папке с переводами
TRANSLATIONS_DIR = "./data/localization"

def load_translations(language):
    file_path = os.path.join(TRANSLATIONS_DIR, f"{language}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                print(file)
                return json.load(file)
        except Exception as e:
            print(f"Ошибка при загрузке переводов: {e}")
            window.evaluate_js(f'ERROR: {e}')
    print(f"Файл переводов для языка '{language}' не найден.")
    window.evaluate_js(f'Файл переводов для языка "{language}" не найден.')
    return {}

def load_queue_from_file():
    """ Загружаем очередь из JSON-файла. """
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8", errors="ignore") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                window.evaluate_js(f'ERROR: {e}')
                return []
    return []

def save_queue_to_file(queue):
    """
    Сохраняет очередь загрузки в JSON-файл.
    """
    try:
        try:
            with open(QUEUE_FILE, "w", encoding="utf-8", errors="ignore") as file:
                json.dump(queue, file, ensure_ascii=False, indent=4)
                print("Очередь загрузки сохранена.")
        except UnicodeEncodeError as e:
            print(f"Ошибка кодировки: {e}. Проблемный символ: {e.object[e.start:e.end]}")
            window.evaluate_js(f'ERROR: {e}')
    except Exception as e:
        print(f"Ошибка при сохранении очереди: {e}")
        window.evaluate_js(f'ERROR: {e}')

# --------------------------------------------------------------------------

# HTML-контент для отображения в окне
html_file_path = os.path.abspath("data/ui/index.html")

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = resource_path(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe")

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = resource_path(str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin"))
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

def format_duration(seconds):
    # Конвертируем секунды в нормальный формат
    hours = int(seconds // 3600)
    minute = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minute:02d}:{seconds:02d}"

def print_video_info(file_path):
    print("Путь: ", file_path)
    if not os.path.exists(file_path):
        return f"Файл не найден: {file_path}"
    
    if not os.access(file_path, os.R_OK):
        return f"Нет прав на чтение файла: {file_path}"
    try:
        # Получает данные 
        probe = ffmpeg.probe(file_path)
        # 
        format_info = probe.get("format", {})
        duration = float(format_info.get("duration", 0))
        bitrate = int(format_info.get("bit_rate", 0)) / 1000 # кбит/с

        # Видеопоток
        video_stream = next(
            (s for s in probe.get("streams", []) if s.get("codec_type") == "video"),
            None
        )

        if not video_stream:
            print("Поток не найден")
            return

        width = video_stream.get("width", "?")
        height = video_stream.get("height", "?")
        codec = video_stream.get("codec_name", "?")
        fps = video_stream.get("r_frame_rate", "?")
        if "/" in fps:
            fps = eval(fps)

        # Аудиопоток
        audio_stream = next(
            (s for s in probe.get("streams", []) if s.get("codec_type") == "audio"),
            None
        )
        audio_codec = audio_stream.get("codec_name", "нет") if audio_stream else "нет"
        audio_bitrate = int(audio_stream.get("bit_rate", 0)) / 1000 if audio_stream else 0
        
        return round(duration), round(bitrate), width, height, codec, round(fps), audio_codec, round(audio_bitrate)
    except ffmpeg.Error as e:
        print(f"Ошибка FFmpeg: {e.stderr.decode()}")
        return f"Ошибка FFmpeg: {e.stderr.decode()}"
    except Exception as e:
        print(f"Ошибка: {e}")
        return f"Ошибка: {e}"

def get_thumbnail_base64(video_path, use_first_frame_if_no_thumbnail=True):
    import base64
    try:
        # Проверяем наличие встроенной обложки
        probe = ffmpeg.probe(video_path)
        has_thumbnail = any(
            stream.get('disposition', {}).get('attached_pic', 0) == 1
            for stream in probe.get('streams', [])
        )
        
        # Если есть встроенная обложка - извлекаем её
        if has_thumbnail:
            out, _ = (
                ffmpeg.input(video_path)
                .output('pipe:', format='image2', vcodec='mjpeg', vframes=1)
                .run(capture_stdout=True, capture_stderr=True)
            )
        # Иначе генерируем превью из первого кадра
        elif use_first_frame_if_no_thumbnail:
            out, _ = (
                ffmpeg.input(video_path, ss='00:00:05')  # Берём кадр в начале видео
                .output('pipe:', format='image2', vcodec='mjpeg', vframes=1)
                .run(capture_stdout=True, capture_stderr=True)
            )
        else:
            return None, "Встроенная обложка не найдена"
        
        # Конвертируем в base64
        img_base64 = base64.b64encode(out).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}", None

    except ffmpeg.Error as e:
        return None, f"Ошибка FFmpeg: {e.stderr.decode()}"
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    
# Класс для определения API
class Api:
    def __init__(self):
        self.download_queue = load_queue_from_file()
        self.download_folder = ''
        self.is_downloading = False  # Флаг для отслеживания состояния загрузки
        self.convert_video_path = ''
        self.ffmpeg_process = None
        self.download_thread = None
        self.download_stop = False
        
    # Возможно больше не понадобитс 
    def remove_emoji_simple(self, text):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # Chinese/Japanese/Korean characters
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # variation selector
            u"\u3030"
            u"\u0259"  # ə
            u"\u0493"  # ғ
            u"\u049B"  # қ
            u"\u04E9"  # ө
            u"\u04B1"  # ұ
            u"\u04AF"  # ү
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)

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
    
    # функция для выбора видео для конвертации
    def openFile(self):
        # Открытие диалогового окна для выбора папки
        root = Tk()
        root.withdraw()  # Скрываем главное окно tkinter
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл",
                filetypes=(("Все файлы", "*.*"), ("Текстовые файлы", "*.txt"), ("Видео", "*.mp4;*.avi"))
            )
        except Exception as e:
            print(f"Ошибка при выборе папки: {e}")
        root.destroy()
        try:
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('converter', {}).get('video_adding')}"')
            window.evaluate_js(f'showSpinner()')
            window.evaluate_js(f'window.updateTranslations({translations})')
            thumbnail, error = get_thumbnail_base64(file_path)
            result = print_video_info(file_path)
            if result is None:
                print("Не удалось получить данные о видео")
            else:
                if result and len(result) == 8:
                    duration, bitrate, width, height, codec, fps, audio_codec, audio_bitrate = result
                else: 
                    print(result)
            file_name = os.path.basename(file_path)
            self.convert_video_path = file_path
            # print(duration, bitrate, codec, fps, audio_codec, audio_bitrate, thumbnail, error, file_name)

            # Формируем данные
            video_data = {
                'duration': duration,
                'bitrate': bitrate,
                'codec': codec,
                'fps': fps,
                'audio_codec': audio_codec,
                'audio_bitrate': audio_bitrate,
                'thumbnail': thumbnail,
                'error': error,
                'file_name': file_name
            }
            window.evaluate_js(f"file_is_input({json.dumps(video_data)})")
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('converter', {}).get('video_add')}"')
            time.sleep(2)
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
        except Exception as e:
            print("Ошибка при выборе видео")
            window.evaluate_js(f'hideSpinner()')
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
            

    # Функция для смены языка
    def switch_language(self, language):
        self.current_language = language
        translations = load_translations(language)
        config.set("Settings", "language", self.current_language)
        save_config(config)
        window.evaluate_js(f'updateApp({update_js},{json.dumps(translations)})')
        window.evaluate_js(f'updateTranslations({json.dumps(translations)})')

    # Функция для смены папки загрузок
    def switch_download_folder(self, folder_path=f'{download_dir}'):
        self.current_folder = folder_path if folder_path is not None else download_dir
        config.set("Settings", "folder_path", self.current_folder)
        save_config(config)
        self.download_folder = self.current_folder
        print("Folder_path: " + folder_path, "download_folder: " + download_folder)
        window.evaluate_js(f'updateDownloadFolder({json.dumps(self.current_folder)})')

    # Функция для выбора папки для загрузки
    def choose_folder(self):
        # Открытие диалогового окна для выбора папки
        root = Tk()
        root.withdraw()  # Скрываем главное окно tkinter
        try:
            folder_path = filedialog.askdirectory()  # Открывает окно выбора папки
            window.evaluate_js(f'updateDownloadFolder({json.dumps(folder_path)})')
            self.switch_download_folder(folder_path)
        except Exception as e:
            print(f"Ошибка при выборе папки: {e}")
        root.destroy()

    # Функция для открытия папки с загрузками
    def open_folder(self):
        try:
            os.startfile(f"{self.download_folder}")
        except Exception as e:
            print(f"Ошибка: {e}")

    # Функция для конвертации видео
    def convert_video(self, output_format):
        try:
            filename = os.path.splitext(os.path.basename(self.convert_video_path))[0]
            output_path = os.path.join(self.download_folder, f"{filename}.{output_format}")

            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get("status", {}).get("converting")}"')
                

            # Получаем длительность видео
            probe = ffmpeg.probe(self.convert_video_path)
            duration = float(probe['format']['duration'])
            # Команда ffmpeg
            command = [
                'ffmpeg',
                '-i', self.convert_video_path,
                '-c:v', 'libx264',  # Пример кодека видео
                '-preset', 'medium',  # Скорость/качество конвертации
                '-c:a', 'aac',  # Пример кодека аудио
                output_path
            ]
           # Запускаем процесс FFmpeg в отдельном потоке
            def run_ffmpeg():
                self.ffmpeg_process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='ignore',  # Явно указываем кодировку UTF-8
                    creationflags=subprocess.CREATE_NO_WINDOW  # Предотвращает открытие консоли
                )
                # Чтение вывода FFmpeg для анализа прогресса
                for line in self.ffmpeg_process.stdout:
                    print(line.strip())  # Для отладки
                    if "time=" in line:
                        try:
                            # Извлекаем текущее время обработки из строки
                            time_str = line.split("time=")[1].split()[0]
                            if time_str == 'N/A':
                                continue
                            hours, minutes, seconds = map(float, time_str.split(":"))
                            current_time = hours * 3600 + minutes * 60 + seconds

                            # Вычисляем процент завершения
                            progress = (current_time / duration) * 100 if duration > 0 else 0
                            progress = min(progress, 100)  # Ограничиваем значение до 100%
                            progress = round(progress, 2)

                            eta_seconds_total = max(duration - current_time, 0)
                            eta_minutes = int(eta_seconds_total // 60)
                            eta_seconds = int(eta_seconds_total % 60)

                            eta_formatted = f"{eta_minutes} {translations['min']} {eta_seconds} {translations['sec']}"

                            # Обновляем прогресс-бар в интерфейсе
                            window.evaluate_js(f'showSpinner()')
                            window.evaluate_js(f'document.getElementById("progress").innerText = "{translations['progress']} {progress}%"')
                            window.evaluate_js(f'document.getElementById("eta").innerText = "{translations['eta']} {eta_formatted}"')
                            window.evaluate_js(f'document.getElementById("progress-fill").style.width = "{progress}%"')
                        except Exception as e:
                            print(f"Ошибка при обработке строки: {line.strip()}. Подробности: {str(e)}")
                            continue

                self.ffmpeg_process.wait()
                if progress > 99:
                    # Уведомляем об успешной конвертации
                    window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get("status", {}).get("convert_success")}"')
                    window.evaluate_js(f'document.getElementById("progress").innerText = "{translations['progress']} 100%"')
                    time.sleep(2)
                    self.open_folder()
                    window.evaluate_js(f'closeVideo()')
                    window.evaluate_js(f'hideSpinner()')
                    window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get("status", {}).get("status_text")}"')
                    window.evaluate_js(f'document.getElementById("eta").innerText = "{translations['eta']} 0 мин 0 сек"')
                    window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')

            # Запускаем процесс конвертации в отдельном потоке
            ffmpeg_thread = Thread(target=run_ffmpeg)
            ffmpeg_thread.start()

            # Уведомляем о начале конвертации
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get("status", {}).get("converting")}"')

            # Ждем завершения потока
            ffmpeg_thread.join()
        except Exception as e:
            print(f"Ошибка при конвертации: {str(e)}")
            window.evaluate_js(f'hideSpinner()')
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get("status", {}).get("convert_error")}: {str(e)}"')
            time.sleep(2)
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get("status", {}).get("status_text")}"')

    def stop_conversion(self):
        # Прерывает процесс конвертации
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:  # Проверяем, что процесс еще работает
            try:
                self.ffmpeg_process.terminate()  # Отправляем сигнал завершения
                print("Конвертация прервана пользователем.")
                window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get("status", {}).get("conversion_stopped")}"')
                time.sleep(2)
                window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
            except Exception as e:
                print(f"Ошибка при попытке прервать конвертацию: {str(e)}")
    
    # Функция для удаления видео из очереди
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

            print(f"Видео удалено из очереди: {video_title}")
            print(video_title)
            # Обновляем интерфейс
            window.evaluate_js(f'removeVideoFromList("{video_title}")')
            
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('removed_from_queue')}: {video_title}"'), time.sleep(3), window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
            time.sleep(2)
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
        except Exception as e:
            print(f"Ошибка при удалении видео из очереди: {str(e)}", video_title)
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('error_removing')}: {str(e)}"'), time.sleep(3), window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
            time.sleep(2)
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')

    # Функция для добавления видео в очередь
    def addVideoToQueue(self, video_url, selected_format, selectedResolution):
        try:
            # Извлекаем информацию о видео (название)
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title_get = info.get('title', 'Неизвестное видео')
                thumbnail_url = info.get('thumbnail', '')
            # video_title = self.remove_emoji_simple(video_title_get.replace('"',"'"))
            video_title = video_title_get.replace('"',"'")


            # Добавляем видео в очередь
            self.download_queue.append((video_url, video_title, selected_format, selectedResolution, thumbnail_url))
            print(f"Видео добавлено в очередь: {video_title} в формате {selected_format} в разрешении {selectedResolution}p")

            # Сохраняем очередь в файл
            save_queue_to_file(self.download_queue)

            # Обновляем интерфейс
            window.evaluate_js(f'addVideoToList("{video_title}", "{thumbnail_url}", "{selected_format}","{selectedResolution}")')
            
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('to_queue')}: {video_title} {translations.get('status', {}).get('in_format')} {selected_format} {translations.get('status', {}).get('in_resolution')} {selectedResolution}p"')
            window.evaluate_js(f'hideSpinner()')
            time.sleep(3)
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
            return
        except Exception as e:
            print(f"Ошибка при добавлении видео в очередь: {str(e)}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('error_adding')}: {str(e)}"')
            window.evaluate_js(f'hideSpinner()')
            time.sleep(3)
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
            return 
        
    # Функция для начала загрузки
    def startDownload(self):
        if self.is_downloading: 
            return f"{translations.get('status', {}).get('downloading_already')}"

        if not self.download_queue:
            return f"{translations.get('status', {}).get('the_queue_is_empty')}"
        
        # Запускаем загрузку
        self.start_next_download()
        window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('downloading')}: {video_title}"') # type: ignore
        return
    
    def stopDownload(self):
        self.is_downloading = False
        self.download_stop = True
        print(self.download_stop)

    # Функция для начала следующей загрузки
    def start_next_download(self):
            if not self.download_stop:
                if not self.download_queue:
                    os.startfile(f"{self.download_folder}")
                    print("Очередь пуста. Загрузка завершена.")
                    # Обновляем статус
                    window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('the_queue_is_empty_download_success')}"')
                    time.sleep(3)
                    window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
                    return

                # Устанавливаем флаг загрузки
                self.is_downloading = True

                save_queue_to_file(self.download_queue)

                # Извлекаем следующее видео из очереди
                video_url, video_title, selected_format, selectedResolution, thumbl = self.download_queue.pop(0)
                print(f"Начинаю загрузку видео: {video_title} в формате {selected_format} в разрешении {selectedResolution}p")
                window.evaluate_js(f'showSpinner()')

                # Обновляем статус в интерфейсе
                window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('downloading')}: {video_title}"')
                window.evaluate_js(f'removeVideoFromList("{video_title}")')

                # Запускаем загрузку видео
                threading.Thread(target=self.download_video, args=(video_url, video_title, selected_format, selectedResolution, download_folder)).start()

                print("Очередь пуста")
            else:
                save_queue_to_file(self.download_queue)
                window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('status_text')}"')
                window.evaluate_js('hideSpinner()')
                self.download_stop = False
    # Функция для загрузки видео с помощью yt-dlp
    def download_video(self, video_url, video_title, selected_format, selectedResolution, download_folder='downloads'):
        try:
            if (selected_format != 'mp3'):
                # Настройки для yt-dlp
                ydl_opts = {
                    'format': f'bestvideo[height<={selectedResolution}]+bestaudio/best[height<={selectedResolution}]',  # Лучшее качество видео и аудио
                    'merge_output_format': selected_format,  # Объединяем видео и аудио в один файл
                    'outtmpl': f'{download_folder}/{video_title}.{selected_format}',  # Путь для сохранения
                    'progress_hooks': [self.progress_hook],  # Добавляем хук для отслеживания прогресса
                    'cookiefile': f'{COOKIES_FILE}',
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
            print(f"Видео успешно загружено: {video_title}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('download_success')}: {video_title}"')
        except Exception as e:
            print(f"Ошибка при загрузке: {str(e)}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{translations.get('status', {}).get('download_error')}: {str(e)}"')

        # Сбрасываем флаг загрузки и запускаем следующую загрузку
        self.is_downloading = False
        self.start_next_download()

    # Хук для отслеживания прогресса
    def progress_hook(self, d):
        if self.is_downloading == True:
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
        else:
            # Загрузка отменена
            window.evaluate_js(f'document.getElementById("progress").innerText = "{translations['progress']} 100%"')
            window.evaluate_js(f'document.getElementById("speed").innerText = "{translations['speed']} 0B/s"')
            window.evaluate_js(f'document.getElementById("eta").innerText = "{translations['eta']} 0 мин 0 сек"')
            window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')
            raise yt_dlp.utils.DownloadCancelled("Загрузка отменена")

if __name__ == "__main__":
    # Создаем экземпляр API
    api = Api()
    api_instance = Api()

    version = get_local_version()

    # Создаем окно с HTML-контентом
    window = webview.create_window(
        f'ClipTide {version}',
        html_file_path,
        js_api=api, # Передаем API для взаимодействия с JavaScript
        height=780,
        width=1000,
        resizable=True,
        text_select=True
    )

    # Загружаем конфигурацию
    config = load_config()

    update = check_for_update()
    update_js = str(update).lower()

    # Используем настройки
    language = config.get("Settings", "language", fallback="ru")
    download_folder = config.get("Settings", "folder_path", fallback="downloads")
    auto_update = config.getboolean("Settings", "auto_update", fallback=False)

    print(f"Язык интерфейса: {language}")
    print(f"Папка загрузки: {download_folder}")
    print(f"Автоматическое обновление: {'Включено' if auto_update else 'Выключено'}")
    print(str(update_js))

    api.download_folder = download_folder
    download_queue = api.download_queue

    # Загружаем параметры при запуске
    translations = load_translations(language)
    window.events.loaded += lambda: window.evaluate_js(f'updateDownloadFolder({json.dumps(download_folder)})')
    window.events.loaded += lambda: window.evaluate_js(f'updateTranslations({json.dumps(translations)})')
    window.events.loaded += lambda: window.evaluate_js(f'window.loadQueue({json.dumps(download_queue)})')
    window.events.loaded += lambda: window.evaluate_js(f'updateApp({update_js}, {json.dumps(translations)})')
    window.events.loaded += lambda: window.evaluate_js(f'setLanguage("{language}")')


    print(translations, download_folder)
    webview.start()