import os
import subprocess
import sys
import yt_dlp
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from pathlib import Path

file = "data.yd"
console = Console()

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

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        "------------------------------------------------------------------------",
        "[1] - Выбрать папку по умолчанию | 'downloads'",
        "[2] - Указать свою папку",
        "------------------------------------------------------------------------",
        "[9] - [bold red]Назад в меню[/]",
    ])

    menu_panel = Panel(
        menu_options,
        title="=== Изменение папки для загрузки ===",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))
    try: 
        choice = int(console.input("\nВведите свой выбор: ").strip())
        if choice == 1:
            folder = "downloads"
            console.print("Выбрана папка по умолчанию: ", folder)
            write_to_file(file, folder)
        elif choice == 2:
            userPath = input("Вставьте путь к папке, в которую будут сохраняться видео: ")
            write_to_file(file, userPath)
        elif choice == 9:
            return
        else:
            console.print("Неверный выбор. Попробуйте снова")
    except ValueError:
            console.print("Пожалуйста, введите только число!")

def settings_menu():
    clear_screen()

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        "------------------------------------------------------------------------",
        f"[1] - Изменить папку загрузки | {folder}",
        f"[2] - Изменить язык приложения | Русский ([red]В разработке[/])",
        "------------------------------------------------------------------------",
        "[9] - [bold red]Назад в меню[/]",
        "[0] - [bold red]Выход[/]"
    ])

    menu_panel = Panel(
        menu_options,
        title="=== Настройки ===",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))

    try:
        choice = int(input("\nВыберите пункт меню: "))
        if choice == 1:
            settingsFolder_menu()
        elif choice == 9:
            return
        elif choice == 0:
            console.print("Выход из программы...")
            exit()
        else:
            console.print("Неверный выбор. Попробуйте снова.")
    except ValueError:
        console.print("Пожалуйста, введите только число!")

folder = read_from_file(file)

def video_settings():
    clear_screen()

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        "-----------------------------------------------",
        "[1] - 720p  || HD",
        "[2] - 1080p || FHD",
        "[3] - 1440p || 2K - если поддерживается видео",
        "[4] - 2160p || 4K - если поддерживается видео",
        "-----------------------------------------------",
        "[9] - [bold red]Назад в меню[/]",
    ])

    menu_panel = Panel(
        menu_options,
        title="=== Выбор разрешения ===",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))

    try:
        choice = int(console.input("\nВыберите пункт меню: ").strip())
        if choice == 1:
            console.print("Загрузчик видео")
            link = console.input("Вставьте ссылку на видео: ")
            download_video(link, "720p", folder)
            open_folder(folder)
        elif choice == 2:
            console.print("Загрузчик видео")
            link = console.input("Вставьте ссылку на видео: ")
            download_video(link, "1080p", folder)
            open_folder(folder)
        elif choice == 3:
            console.print("Загрузчик видео")
            link = console.input("Вставьте ссылку на видео: ")
            download_video(link, "1440p", folder)
            open_folder(folder)
        elif choice == 4:
            console.print("Загрузчик видео")
            link = console.input("Вставьте ссылку на видео: ")
            download_video(link, "2160p", folder)
            open_folder(folder)
        elif choice == 9:
            return
        else:
            console.print("Неверный выбор. Попробуйте снова")
    except ValueError:
        console.print("Пожалуйста, введите только число!")

def audio_menu():
    clear_screen()

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        "----------------------------------",
        "[0] - [bold red]Для отмены[/]",
        "----------------------------------",
    ])

    menu_panel = Panel(
        menu_options,
        title="=== Загрузка аудио ===",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))
    link = console.input("Вставьте ссылку на видео: ".strip())
    if link == '0':
        return
    else:
        download_audio_as_mp3(link, folder)
        open_folder(folder)

def main_menu():
    while True:
        clear_screen()
        title = Text("Добро пожаловать в YouTube Downloader", justify="center", style="bold red")
        console.print(Align.center(Panel(title, expand=False, border_style="green")))
        menu_options = "\n".join([
            "\nДля продолжения выберите пункт меню вводя нужные цифры на клавиатуре",
            "------------------------------------------------------------------------",
            "[1] - Скачать аудио в формате .mp3 --- Максимальное качество звука",
            "[2] - Скачать видео в формате .mp4 --- HD - 4K",
            "------------------------------------------------------------------------",
            "[3] - Настройки",
            "------------------------------------------------------------------------",
            "[0] - [bold red]Выход из программы[/]",
        ])

        menu_panel = Panel(
            menu_options,
            title="=== Главное меню ===",
            title_align="center",
            border_style="green",
            width=240,
            expand=False,
        )

        console.print(Align(menu_panel, align="center"))

        try:
            choice = int(console.input("\nВыберите пункт меню: ").strip())
            if choice == 1:
                audio_menu()
            elif choice == 2:
                video_settings()
            elif choice == 3:
                settings_menu()
            elif choice == 0:
                console.print("Выход из программы...")
                break
            else:
                console.print("Неверный выбор. Попробуйте снова.")
        except ValueError:
            console.print("Пожалуйста, введите только число.")

if __name__ == "__main__":
    main_menu()