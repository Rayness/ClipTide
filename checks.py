import os
import subprocess
import sys
import zipfile
import urllib.request
from pathlib import Path

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

# Функция для отображения прогресса
def download_progress_hook(count, block_size, total_size):
    # Вычисляем сколько процентов уже загружено
    if total_size > 0:
        percent = int(count * block_size * 100 / total_size)
        # Выводим прогресс
        bar = ('#' * (percent // 2)).ljust(50)
        sys.stdout.write(f"\r[{bar}] {percent}%")
        sys.stdout.flush()

def install_ffmpeg():
    # Проверяем, установлен ли FFmpeg, и если да, пропускаем установку
    try:
        os.makedirs(ffmpeg_dir, exist_ok=True)
        subprocess.check_call([str(ffmpeg_exe), "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("FFmpeg уже установлен.")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg не найден, устанавливаем...")

    # Скачиваем архив FFmpeg
    try:    
        zip_path = ffmpeg_dir / "ffmpeg.7z"
        print("Скачиваем FFmpeg...", zip_path)
        urllib.request.urlretrieve(FFMPEG_URL, zip_path, reporthook=download_progress_hook)
    except:
        print("Ошибка загрузки архива")

    # Распаковываем архив
    print("\n Распаковываем FFmpeg...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(ffmpeg_dir)

    # Удаляем скачанный архив
    zip_path.unlink()


def install_yt_dlp():
    try:
        import yt_dlp
        print("yt-dlp уже установлен.")
    except ImportError:
        print("Устанавливаю yt-dlp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])

def install_rich():
    try:
        import rich
        print("rich уже установлен")
    except ImportError:
        print("Устанавливаю rich...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])

def main():
    install_yt_dlp()
    install_ffmpeg()
    install_rich()


if __name__ == "__main__":
    main()