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
html_file_path = os.path.abspath("gui/index.html")

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

# Класс для определения API
class Api:
    def __init__(self):
        self.download_queue = []  # Очередь для загрузки видео
        self.is_downloading = False  # Флаг для отслеживания состояния загрузки

    def addVideoToQueue(self, video_url):
        try:
            # Извлекаем информацию о видео (название)
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'Неизвестное видео')

            # Добавляем видео в очередь
            self.download_queue.append((video_url, video_title))
            print(f"Видео добавлено в очередь: {video_title}")

            # Обновляем интерфейс
            window.evaluate_js(f'addVideoToList("{video_title}")')

            return f"Видео добавлено в очередь: {video_title}"
        except Exception as e:
            print(f"Ошибка при добавлении видео в очередь: {str(e)}")
            return f"Ошибка при добавлении видео: {str(e)}"

    def startDownload(self):
        if self.is_downloading:
            return "Загрузка уже запущена."

        if not self.download_queue:
            return "Очередь пуста. Нечего загружать."

        # Запускаем загрузку
        self.start_next_download()
        return "Загрузка начата."

    def start_next_download(self):
        if not self.download_queue:
            print("Очередь пуста. Загрузка завершена.")
            window.evaluate_js('document.getElementById("status").innerText = "Очередь пуста. Загрузка завершена."')
            return

        # Устанавливаем флаг загрузки
        self.is_downloading = True

        # Извлекаем следующее видео из очереди
        video_url, video_title = self.download_queue.pop(0)
        print(f"Начинаю загрузку видео: {video_title}")

        # Обновляем статус в интерфейсе
        window.evaluate_js(f'document.getElementById("status").innerText = "Загружаю: {video_title}"')
        window.evaluate_js(f'removeVideoFromList("{video_title}")')

        # Запускаем загрузку видео
        threading.Thread(target=self.download_video, args=(video_url, video_title)).start()

    def download_video(self, video_url, video_title):
        try:
            # Настройки для yt-dlp
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',  # Лучшее качество видео и аудио
                'merge_output_format': 'mp4',  # Объединяем видео и аудио в один файл
                'outtmpl': 'downloads/%(title)s.%(ext)s',  # Путь для сохранения
                'progress_hooks': [self.progress_hook],  # Добавляем хук для отслеживания прогресса
            }

            # Загружаем видео
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            print(f"Видео успешно загружено: {video_title}")
            window.evaluate_js(f'document.getElementById("status").innerText = "Видео успешно загружено: {video_title}"')
        except Exception as e:
            print(f"Ошибка при загрузке: {str(e)}")
            window.evaluate_js(f'document.getElementById("status").innerText = "Ошибка при загрузке: {str(e)}')

        # Сбрасываем флаг загрузки и запускаем следующую загрузку
        self.is_downloading = False
        self.start_next_download()

    # Хук для отслеживания прогресса
    # Хук для отслеживания прогресса
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Получаем данные о прогрессе
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes', 1)  # Избегаем деления на ноль
            speed = d.get('speed', '0B/s')
            eta = d.get('eta', 0)  # Оставшееся время в секундах

            # Вычисляем прогресс
            progress = (downloaded_bytes / total_bytes) * 100 if total_bytes > 0 else 0
            progress = round(progress, 2)  # Округляем до двух знаков после запятой

            # Преобразуем ETA в читаемый формат
            eta_minutes = eta // 60
            eta_seconds = eta % 60
            eta_formatted = f"{int(eta_minutes)} мин {int(eta_seconds)} сек"

 # Преобразуем скорость в Мбайты/сек
            speed_mbps = speed / (1024 * 1024) if speed else 0
            speed_formatted = f"{speed_mbps:.2f} MB/s"  # Форматируем до двух знаков после запятой

            # Выводим отладочную информацию
            print(f"Progress: {progress}%, Speed: {speed_formatted}, ETA: {eta_formatted}")

            # Обновляем интерфейс
            window.evaluate_js(f'document.getElementById("progress").innerText = "Прогресс: {progress}%"')
            window.evaluate_js(f'document.getElementById("speed").innerText = "Скорость: {speed_formatted}"')
            window.evaluate_js(f'document.getElementById("eta").innerText = "Осталось: {eta_formatted}"')
        elif d['status'] == 'finished':
            # Загрузка завершена
            window.evaluate_js('document.getElementById("progress").innerText = "Прогресс: 100%"')
            window.evaluate_js('document.getElementById("speed").innerText = "Скорость: 0B/s"')
            window.evaluate_js('document.getElementById("eta").innerText = "Осталось: 0 мин 0 сек"')

if __name__ == "__main__":
    # Создаем экземпляр API
    api = Api()

    # Создаем окно с HTML-контентом
    window = webview.create_window(
        'YouTube Video Downloader',
        html_file_path,
        js_api=api  # Передаем API для взаимодействия с JavaScript
    )

    webview.start()