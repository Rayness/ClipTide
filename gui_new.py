import os
import sys
import threading
sys.path.insert(0, "./libs")
import yt_dlp
import webview
from pathlib import Path

# HTML-контент для отображения в окне
html_content = "GUI/index.html"

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

resolusion = "720p"

# Класс для определения API
class Api:

    def downloadVideo(self, video_url, resolution):
        def download():
            try:
                # Настройки для yt-dlp
                ydl_opts = {
                    'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',  # Лучшее качество видео
                    'outtmpl': 'downloads/%(title)s.%(ext)s',  # Путь для сохранения
                    'merge_output_format': 'mp4',
                    'quiet': False,  # Показывает прогресс в консоли
                }

                # Загружаем видео
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    video_title = info.get('title', 'Видео')

                # Возвращаем сообщение об успешной загрузке
                window.evaluate_js(f'document.getElementById("status").innerText = "Видео успешно загружено: {video_title}"')
            except Exception as e:
                # Логируем ошибку в консоль
                print(f"Ошибка при загрузке: {str(e)}")
                # Отображаем ошибку в интерфейсе
                window.evaluate_js(f'document.getElementById("status").innerText = "Ошибка при загрузке: {str(e)}"')

        # Запускаем загрузку в отдельном потоке
        threading.Thread(target=download).start()

        return "Загрузка начата..."

if __name__ == "__main__":
    # Создаем экземпляр API
    api = Api()

    # Создаем окно с HTML-контентом
    window = webview.create_window(
        'YT-Downloader',
        'GUI/index.html',
        js_api=api  # Передаем API для взаимодействия с JavaScript
    )

    # Запускаем приложение
    webview.start()