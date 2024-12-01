import os
import subprocess
import sys
import yt_dlp
from pathlib import Path

file = "data.yd"

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


def read_from_file(file_name):
    try:
        with open(file_name, "r") as file:
            content = file.read()
        print(f"Данные из файла '{file_name}':\n{content}")
        return content
    except FileNotFoundError:
        print(f"Файл '{file_name}' не найден.")
        return None
    except Exception as e:
        print(f"Ошибка при чтении: {e}")
        return None

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

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def settingsFolder_menu():
    clear_screen()
    print("Изменение папки для загрузки")
    print("")
    print("------------------------------------------------------------------------")
    print("[1] - Выбрать папку по умолчанию")
    print("[2] - Указать свою папку")
    print("------------------------------------------------------------------------")
    print("[0] - Назад в меню")
    print("")
    try: 
        choice = int(input("Введите свой выбор: "))
        if choice == 1:
            folder = "downloads"
            print("Выбрана папка по умолчанию: ", folder)
            write_to_file(file, folder)
        elif choice == 2:
            print("Текущая папка для сохранения: ", folder)
            userPath = input("Вставьте путь к папке, в которую будут сохраняться видео: ")
            write_to_file(file, userPath)
        elif choice == 0:
            return
        else:
            print("Неверный выбор. Попробуйте снова")
    except ValueError:
            print("Пожалуйста, введите только число!")

def settings_menu():
    clear_screen()
    print("")
    print("Настройки")
    print("------------------------------------------------------------------------")
    print("[1] - Изменить папку загрузки | ",folder )
    print("[2] - Изменить язык приложения | Русский")
    print("------------------------------------------------------------------------")
    print("[0] - Назад в меню")
    print("[00] - Выход")
    print("")
    try:
        choice = int(input("Выберите пункт меню: "))
        if choice == 1:
            settingsFolder_menu()
        elif choice == 0:
            return
        elif choice == 00:
            print("Выход из программы...")
            exit()
        else:
            print("Неверный выбор. Попробуйте снова.")
    except ValueError:
        print("Пожалуйста, введите только число!")

folder = read_from_file(file)

def video_settings():
    clear_screen()
    print("Выберите предпочтительное разрешение")
    print("-----------------------------------------------")
    print("[1] - 720p || HD")
    print("[2] - 1080p || FHD")
    print("[3] - 1440p || 2K - если поддерживается видео")
    print("[4] - 2160p || 4K - если поддерживается видео")
    print("-----------------------------------------------")
    print("[0] - Назад в меню")
    try:
        choice = int(input("Выберите пункт меню: "))
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
        elif choice == 0:
            return
        else:
            print("Неверный выбор. Попробуйте снова")
    except ValueError:
        print("Пожалуйста, введите только число!")

def audio_menu():
    clear_screen()
    print("\nЗагрузчик аудио")
    print("----------------------------------")
    print("\n[0] - Для отмены")
    print("----------------------------------")
    link = input("Вставьте ссылку на видео: ")
    if link == '0':
        return
    else:
        download_audio_as_mp3(link, folder)
        open_folder(folder)

def main_menu():
    while True:
        clear_screen()
        print("\033[31m\nДобро пожаловать в YouTube Downloader\033[0m")
        print("\033[32m\nДля продолжения выберите пункт меню вводя нужные цифры на клавиатуре\033[0m")
        print("------------------------------------------------------------------------")
        print("\033[34m[1]\033[0m - Скачать аудио в формате .mp3 --- Максимальное качество звука")
        print("\033[34m[2]\033[0m - Скачать видео в формате .mp4 --- HD - 4K")
        print("------------------------------------------------------------------------")
        print("\033[31m[3]\033[0m - Настройки")
        print("------------------------------------------------------------------------")
        print("\033[31m[0]\033[0m - Выход из программы")
        try:
            choice = int(input("\nВыберите пункт меню: "))
            if choice == 1:
                audio_menu()
            elif choice == 2:
                video_settings()
            elif choice == 3:
                settings_menu()
            elif choice == 0:
                print("Выход из программы...")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
        except ValueError:
            print("Пожалуйста, введите только число.")

if __name__ == "__main__":
    main_menu()