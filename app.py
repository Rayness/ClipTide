import yt_dlp
import os
import subprocess
import sys
import zipfile
import urllib.request
from pathlib import Path

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

def check_python_installed():
    try:
        # Попробуем вызвать python --version
        result = subprocess.run([sys.executable, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Проверим код возврата
        if result.returncode == 0:
            print(f"Python установлен: {result.stdout.decode().strip()}")
            return
        else:
            print("Python не найден.")
    except FileNotFoundError:
        print("Python не найден в системе, будет произведена установка")

        python_url = "https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe"
        installer_path = "python_installer.exe"

        print("Скачивание установщика Python...")
        # Скачиваем файл
        urllib.request.urlretrieve(python_url, installer_path)
        print("Установщик скачан.")

        print("Запуск установщика Python...")
        # Запуск установщика с параметрами
        subprocess.run([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"], check=True)
        print("Python установлен.")



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

def main():
    install_yt_dlp()
    install_ffmpeg()
    # Добавляем FFmpeg в PATH
    ffmpeg_bin_path = str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin")
    os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
    print("FFmpeg установлен и добавлен в PATH.")

    # Здесь основной код для скачивания с помощью yt-dlp
    # url = "https://www.youtube.com/watch?v=your_video_id"
    # yt_dlp.YoutubeDL({'format': 'bestaudio', 'outtmpl': '%(title)s.%(ext)s'}).download([url])

def progress_hook(d):
    if d['status'] == 'downloading':
        # Рассчитываем процент скачанного контента
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        # Выводим прогресс
        print(f"Загрузка: {percent:.2f}% - {d['downloaded_bytes']} из {d['total_bytes']} байт", end='\r')
    elif d['status'] == 'finished':
        print("\nЗагрузка завершена!")

def download_audio_as_mp3(url):
    ydl_opts = {
        'format': 'bestaudio/best',  # Загрузить лучшее качество аудио
        'outtmpl': '%(title)s.%(ext)s',  # Сохранять с оригинальным названием
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

if __name__ == "__main__":
    check_python_installed()
    main()
    import sys
    if len(sys.argv) > 1:
        download_audio_as_mp3(sys.argv[1])
    else:
        print("Пожалуйста, введите URL видео YouTube.")
