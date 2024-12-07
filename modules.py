import os
import subprocess
import sys
sys.path.insert(0, "./libs")
import yt_dlp
import json
from queue import Queue
import configparser
from pathlib import Path

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

lang, path = load_config()

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

def load_translations(language):
    with open(f"localization/{language}.json", "r", encoding="utf-8") as file:
        return json.load(file)

translations = load_translations(lang)

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
print(f"{translations["ffmpeg"]}")

#Функция для указания пути к файлу
def downloadPath():
    os.environ

#Функция для создания папки
def create_folder(folder_name):
    try:
        os.makedirs(folder_name, exist_ok=True)
        print(f"{translations['create_folder:success']}")
    except Exception as e:
        print(f"{translations['create_folder:error']}: {e}")

# Функция для открытия папки
def open_folder(folder_path):
    try:
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder_path])
        else:
            subprocess.run(["xdg-open", folder_path])
        print(f"{translations['open_folder:success']}: {folder_path}")
    except Exception as e:
        print(f"{translations['open_folder:error']}: {e}")

def progress_hook(d):
    if d['status'] == 'downloading':
        # Рассчитываем процент скачанного контента
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        # Выводим прогресс
        print(f"{translations['progress_hook:process']}: {percent:.2f}% - {d['downloaded_bytes']} из {d['total_bytes']} байт", end='\r')
    elif d['status'] == 'finished':
        print(f"\n{translations['progress_hook:success']}")

def download_audio_as_mp3(url, output_folder):
    ydl_opts = {
        'format': 'bestaudio/best',  # Загрузить лучшее качество аудио
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),  # Сохранять с оригинальным названием
        'postprocessors': [
            {  # Первый этап: скачивание аудио
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
        ],
        'progress_hooks': [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_video(url, resolution, output_folder):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': False,  # Показывает прогресс в консоли
        'socket_timeout': 60,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
