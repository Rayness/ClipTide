import os
import sys
import threading
sys.path.insert(0, "./libs")
import yt_dlp
import webview
import time
import queue
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
    def __init__(self):
        self.progress_queue = queue.Queue()  # Очередь для передачи прогресса

    def downloadVideo(self, video_url, resolution):
        def download():
            try:
                # Настройки для yt-dlp
                ydl_opts = {
                    'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',  # Лучшее качество видео и аудио
                    'merge_output_format': 'mp4',  # Объединяем видео и аудио в один файл
                    'outtmpl': 'downloads/%(title)s.%(ext)s',  # Путь для сохранения
                    'progress_hooks': [self.progress_hook],  # Добавляем хук для отслеживания прогресса
                }

                # Загружаем видео
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    video_title = info.get('title', 'Видео')

                # Возвращаем сообщение об успешной загрузке
                self.progress_queue.put(("status", f"Видео успешно загружено: {video_title}"))
            except Exception as e:
                # Логируем ошибку в консоль
                print(f"Ошибка при загрузке: {str(e)}")
                # Отображаем ошибку в интерфейсе
                self.progress_queue.put(("status", f"Ошибка при загрузке: {str(e)}"))

        # Запускаем загрузку в отдельном потоке
        threading.Thread(target=download).start()

        return "Загрузка начата..."

    # Хук для отслеживания прогресса
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Получаем процент загрузки
            progress = d.get('_percent_str', '0%').replace('%', '')
            try:
                progress = float(progress)
            except ValueError:
                progress = 0

            # Помещаем прогресс в очередь
            self.progress_queue.put(("progress", progress))
        elif d['status'] == 'finished':
            # Загрузка завершена
            self.progress_queue.put(("progress", 100))

    # Метод для обработки очереди событий
    def process_queue(self):
        while not self.progress_queue.empty():
            event_type, data = self.progress_queue.get()
            if event_type == "progress":
                # Обновляем прогресс в интерфейсе
                window.evaluate_js(f'window.updateProgress({data})')
            elif event_type == "status":
                # Обновляем статус в интерфейсе
                window.evaluate_js(f'document.getElementById("status").innerText = "{data}"')

if __name__ == "__main__":
    # Создаем экземпляр API
    api = Api()

    # Создаем окно с HTML-контентом
    window = webview.create_window(
        'YouTube Video Downloader',
        'gui/index.html',
        js_api=api  # Передаем API для взаимодействия с JavaScript
    )

    # Запускаем приложение с обработкой очереди событий
    def update_gui():
        while True:
            api.process_queue()
            time.sleep(0.1)  # Небольшая задержка для снижения нагрузки на CPU

    threading.Thread(target=update_gui, daemon=True).start()
    webview.start()