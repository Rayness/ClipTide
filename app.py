import os
import subprocess
import sys
import yt_dlp
from pathlib import Path

folder = "downloads"

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
print("FFmpeg установлен и добавлен в PATH.")

#Функция для указания пути к файлу
def downloadPath():
    os.environ

#Функция для создания папки
def create_folder(folder_name):
    try:
        os.makedirs(folder_name, exist_ok=True)
        print("Папка создана")
    except Exception as e:
        print("Ошибка при создании папки: {e}")

# Функция для открытия папки
def open_folder(folder_path):
    try:
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder_path])
        else:
            subprocess.run(["xdg-open", folder_path])
        print(f"Открыта папка: {folder_path}")
    except Exception as e:
        print(f"Ошибка при открытии папки: {e}")

# Функция для создания пустого файла
def create_file(file_name):
    try:
        with open(file_name, "w") as f:
            pass
        print(f"Файл '{file_name}' создан.")
    except Exception as e:
        print(f"Ошибка при создании файла: {e}")

# Функция для записи данных в файл
def write_to_file(file_name, content):
    try:
        with open(file_name, "w") as f:
            f.write(content)
        print(f"Данные записаны в файл '{file_name}'.")
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")

def progress_hook(d):
    if d['status'] == 'downloading':
        # Рассчитываем процент скачанного контента
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        # Выводим прогресс
        print(f"Загрузка: {percent:.2f}% - {d['downloaded_bytes']} из {d['total_bytes']} байт", end='\r')
    elif d['status'] == 'finished':
        print("\nЗагрузка завершена!")

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

def video_settings():
    print("Выберите предпочтительное разрешение")
    print("")
    print("[1] - 720p || HD")
    print("[2] - 1080p || FHD")
    print("[3] - 1440p || 2K - если поддерживается видео")
    print("[4] - 2160p || 4K - если поддерживается видео")
    try:
        choice = int(input("Введите цифру для продолжения: "))
        if choice == 1:
            print("Загрузчик видео")
            link = input("Вставьте ссылку на видео: ")
            download_video(link, "720p", folder)
            open_folder(folder)
        elif choice == 2:
            print("Загрузчик видео")
            link = input("Вставьте ссылку на видео: ")
            download_video(link, "1080p", folder)
            open_folder(folder)
        elif choice == 3:
            print("Загрузчик видео")
            link = input("Вставьте ссылку на видео: ")
            download_video(link, "1440p", folder)
            open_folder(folder)
        elif choice == 4:
            print("Загрузчик видео")
            link = input("Вставьте ссылку на видео: ")
            download_video(link, "2160p", folder)
            open_folder(folder)
        else:
            print("Неверный выбор. Попробуйте снова")
    except ValueError:
        print("Пожалуйста, введите только число!")

def main():
    while True:
        print("")
        print("\033[31mДобро пожаловать в YouTube Downloader\033[0m")
        print("")
        print("\033[32mДля продолжения выберите пункт меню вводя нужные цифры на клавиатуре\033[0m")
        print("------------------------------------------------------------------------")
        print("\033[34m[1]\033[0m - Скачать аудио в формате .mp3 --- Максимальное качество звука")
        print("\033[34m[2]\033[0m - Скачать видео в формате .mp4 --- HD - 4K")
        print("------------------------------------------------------------------------")
        print("\033[31m[3]\033[0m - Настройки")
        print("------------------------------------------------------------------------")
        print("\033[31m[0]\033[0m - Выход из программы")
        print("")
        try:
            choice = int(input("Введите цифру: "))
            if choice == 1:
                print("Загрузчик аудио")
                link = input("Вставьте ссылку на видео: ")
                download_audio_as_mp3(link, folder)
                open_folder(folder)
            elif choice == 2:
                video_settings()
            elif choice == 0:
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
        except ValueError:
            print("Пожалуйста, введите только число.")

if __name__ == "__main__":
    main()