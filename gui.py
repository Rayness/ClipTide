import sys
import tkinter as tk
import os
sys.path.insert(0, "./libs")
from tkinter import ttk, filedialog
import threading
import yt_dlp
import json
from scripts.utils import load_translations
from pathlib import Path

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

translations = load_translations('en')

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path


translations = load_translations('en')

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("500x450")

        # Очередь загрузок
        self.download_queue = []

        # Поле ввода ссылки
        self.url_label = ttk.Label(root, text="Введите ссылку на видео:")
        self.url_label.pack(pady=5)

        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Кнопка для добавления в очередь
        self.add_to_queue_button = ttk.Button(root, text="Добавить в очередь", command=self.add_to_queue)
        self.add_to_queue_button.pack(pady=5)

        # Очередь загрузок (отображение)
        self.queue_label = ttk.Label(root, text="Очередь загрузок:")
        self.queue_label.pack(pady=5)

        self.queue_listbox = tk.Listbox(root, height=10, width=50)
        self.queue_listbox.pack(pady=5)

        # Кнопка для начала загрузки
        self.start_download_button = ttk.Button(root, text="Начать загрузку", command=self.start_download_thread)
        self.start_download_button.pack(pady=10)

        # Кнопка для открытия меню настроек
        self.settings_button = ttk.Button(root, text="Настройки", command=self.open_settings)
        self.settings_button.pack(pady=5)

        # Прогресс-бар
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        # Метка для статуса
        self.status_label = ttk.Label(root, text="Статус: Готов")
        self.status_label.pack(pady=5)

    def downloading(self, url, output_folder):
        def progress_hook(d):
            if d['status'] == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)  # Избегаем деления на ноль
                progress = int((downloaded_bytes / total_bytes) * 100)
                self.update_progress(progress, f"Скачивается... {progress}%")
            elif d['status'] == 'finished':
                self.update_progress(100, "Загрузка завершена!")
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
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.update_progress(0, f"Ошибка: {str(e)}")

    def add_to_queue(self):
        url = self.url_entry.get().strip()
        if url:
            self.download_queue.append(url)
            self.queue_listbox.insert(tk.END, url)
            self.url_entry.delete(0, tk.END)
        else:
            self.status_label.config(text="Статус: Пожалуйста, введите ссылку!")

    def start_download_thread(self):
        thread = threading.Thread(target=self.start_download)
        thread.start()

    def start_download(self):
        while self.download_queue:
            url = self.download_queue.pop(0)
            output_folder = 'downloads'
            self.queue_listbox.delete(0)
            self.downloading(url, output_folder)

        self.status_label.config(text="Статус: Все загрузки завершены!")

    def update_progress(self, value, status_text):
        """Обновление прогресса и текста."""
        self.progress['value'] = value
        self.status_label.config(text=status_text)
        self.root.update_idletasks()

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("300x200")

        # Пример настроек
        ttk.Label(settings_window, text="Папка для сохранения:").pack(pady=5)
        self.save_path = tk.StringVar()
        self.save_path.set()
        
        save_path_entry = ttk.Entry(settings_window, textvariable=self.save_path, width=30)
        save_path_entry.pack(pady=5)

        browse_button = ttk.Button(settings_window, text="Обзор", command=self.browse_folder)
        browse_button.pack(pady=5)

        ttk.Button(settings_window, text="Сохранить", command=settings_window.destroy).pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)
        return folder

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
