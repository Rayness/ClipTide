import os
import subprocess
import sys
import yt_dlp
import json
import configparser
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from pathlib import Path

config_file = "config.ini"

# Функция для записи данных в INI-файл
def save_config(language, folder_path):
    config = configparser.ConfigParser()
    config['Settings'] = {
        'language': language,
        'folder_path': folder_path
    }
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

console = Console()

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

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def restart_program():
    """Перезапускает текущий скрипт."""
    print("Перезапуск приложения...")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def settingsLanguage_menu():
    clear_screen()

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        f"[yellow bold]{translations['settingsLanguage_menu:info']}[/]",
        "------------------------------------------------------------------------",
        f"[1] - {translations['settingsLanguage_menu:lang:ru']}",
        f"[2] - {translations['settingsLanguage_menu:lang:en']}",
        "------------------------------------------------------------------------",
        f"[9] - [bold red]{translations['menu:back']}[/]",
        f"[0] - [bold red]{translations['menu:exit']}[/]"
    ])

    menu_panel = Panel(
        menu_options,
        title=f"{translations['settingsLanguage_menu:title']}",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))

    try:
        choice = int(console.input(f"\n{translations['choice_input']}: ").strip())
        if choice == 1:
            lang = "ru"
            save_config(lang, path)
            restart_program()
        elif choice == 2:
            lang = "en"
            save_config(lang, path)
            restart_program()
        elif choice == 9:
            return
        elif choice == 0:
            exit()
        else:
            console.print(f"{translations['error_choice']}")
    except ValueError:
            console.print(f"{translations['error_value']}")

def settingsFolder_menu():
    clear_screen()

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        f"[yellow bold]{translations['settingsFolder_menu:menu:info']}[/]",
        "------------------------------------------------------------------------",
        f"[1] - {translations['settingsFolder_menu:menu:defoult_folder']} | 'downloads'",
        f"[2] - {translations['settingsFolder_menu:menu:select_folder']}",
        "------------------------------------------------------------------------",
        f"[9] - [bold red]{translations['menu:back']}[/]",
        f"[0] - [bold red]{translations['menu:exit']}[/]"
    ])

    menu_panel = Panel(
        menu_options,
        title=f"{translations['settingsFolder_menu:menu:panel:title']}",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))
    try: 
        choice = int(console.input(f"\n{translations['choice_input']}: ").strip())
        if choice == 1:
            folder = "downloads"
            console.print(f"{translations['settingsFolder_menu:folder:defoult_folder']}: ", folder)
            save_config(lang, folder)
            restart_program()
        elif choice == 2:
            userPath = input(f"{translations['settingsFolder_menu:folder:select_folder']}: ")
            save_config(lang, userPath)
            restart_program()
        elif choice == 9:
            return
        elif choice == 0:
            exit()
        else:
            console.print(f"{translations['error_choice']}")
    except ValueError:
            console.print(f"{translations['error_value']}")

def settings_menu():
    clear_screen()

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        "------------------------------------------------------------------------",
        f"[1] - {translations['settings_menu:menu:change_folder']}  | ([red]{path}[/])",
        f"[2] - {translations['settings_menu:menu:change_language']} | ([red]{lang}[/])",
        "------------------------------------------------------------------------",
        f"[9] - [bold red]{translations['menu:back']}[/]",
        f"[0] - [bold red]{translations['menu:exit']}[/]"
    ])

    menu_panel = Panel(
        menu_options,
        title=f"{translations['settings_menu:menu:panel:title']}",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))

    try:
        choice = int(input(f"\n{translations['choice_input']}: "))
        if choice == 1:
            settingsFolder_menu()
        elif choice == 2:
            settingsLanguage_menu()
        elif choice == 9:
            return
        elif choice == 0:
            console.print(f"{translations['exit_app']}")
            exit()
        else:
            console.print(f"{translations['error_choice']}")
    except ValueError:
        console.print(f"{translations['error_value']}")

def video_settings():
    clear_screen()

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        "-----------------------------------------------",
        f"[1] - 720p  || HD",
        f"[2] - 1080p || FHD",
        f"[3] - 1440p || 2K - {translations['video_settings:menu:if_true']}",
        f"[4] - 2160p || 4K - {translations['video_settings:menu:if_true']}",
        "-----------------------------------------------",
        f"[9] - [bold red]{translations['menu:back']}[/]",
        f"[0] - [bold red]{translations['menu:exit']}[/]"
    ])

    menu_panel = Panel(
        menu_options,
        title=f"{translations['video_settings:menu:panel:title']}",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))

    try:
        choice = int(console.input(f"\n{translations['choice_input']}: ").strip())
        if choice == 1:
            console.print(f"{translations['video_settings:menu:video_loader']}")
            link = console.input(f"{translations['input_link']}: ")
            download_video(link, "720p", path)
            open_folder(path)
        elif choice == 2:
            console.print(f"{translations['video_settings:menu:video_loader']}")
            link = console.input(f"{translations['input_link']}: ")
            download_video(link, "1080p", path)
            open_folder(path)
        elif choice == 3:
            console.print(f"{translations['video_settings:menu:video_loader']}")
            link = console.input(f"{translations['input_link']}: ")
            download_video(link, "1440p", path)
            open_folder(path)
        elif choice == 4:
            console.print(f"{translations['video_settings:menu:video_loader']}")
            link = console.input(f"{translations['input_link']}: ")
            download_video(link, "2160p", path)
            open_folder(path)
        elif choice == 9:
            return
        else:
            console.print(f"{translations['error_choice']}")
    except ValueError:
        console.print(f"{translations['error_value']}")

def audio_menu():
    clear_screen()

    title = Text("YouTube Downloader", justify="center", style="bold red")
    console.print(Align.center(Panel(title, expand=False, border_style="green")))

    menu_options = "\n".join([
        "----------------------------------",
        f"[0] - [bold red]{translations['audio_menu:menu:cancel']}[/]",
        "----------------------------------",
    ])

    menu_panel = Panel(
        menu_options,
        title=f"{translations['audio_menu:menu:panel:title']}",
        title_align="center",
        border_style="green",
        width=240,
        expand=False,
    )

    console.print(Align(menu_panel, align="center"))
    link = console.input(f"{translations['input_link']}: ".strip())
    if link == '0':
        return
    else:
        download_audio_as_mp3(link, path)
        open_folder(path)

def main_menu():
    while True:
        clear_screen()
        title = Text(f"{translations['main_menu:title']} YouTube Downloader", justify="center", style="bold red")
        console.print(Align.center(Panel(title, expand=False, border_style="green")))
        menu_options = "\n".join([
            f"\n[green]{translations['main_menu:menu:help']}[/]",
            "------------------------------------------------------------------------",
            f"[1] - {translations['main_menu:menu:download_mp3']}",
            f"[2] - {translations['main_menu:menu:download_mp4']}",
            "------------------------------------------------------------------------",
            f"[3] - {translations['main_menu:menu:settings']}",
            "------------------------------------------------------------------------",
            f"[0] - [bold red]{translations['main_menu:menu:exit']}[/]",
        ])

        menu_panel = Panel(
            menu_options,
            title=f"{translations['main_menu:menu:panel:title']}",
            title_align="center",
            border_style="green",
            width=240,
            expand=False,
        )

        console.print(Align(menu_panel, align="center"))

        try:
            choice = int(console.input(f"\n{translations['choice_input']}: ").strip())
            if choice == 1:
                audio_menu()
            elif choice == 2:
                video_settings()
            elif choice == 3:
                settings_menu()
            elif choice == 0:
                console.print(f"{translations['exit_app']}")
                break
            else:
                console.print(f"{translations['error_choice']}")
        except ValueError:
            console.print(f"{translations['error_value']}")

if __name__ == "__main__":
    main_menu()