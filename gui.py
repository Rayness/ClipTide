import sys
import tkinter as tk
import os
sys.path.insert(0, "./libs")
from tkinter import IntVar, ttk, filedialog
import webview
import threading
import yt_dlp
from scripts.utils import load_translations
from pathlib import Path

ffmpeg_dir = Path("ffmpeg")  # Директория, куда распакуем FFmpeg
ffmpeg_exe = ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin" / "ffmpeg.exe"

translations = load_translations('en')

audio_dl = False

import webview

# HTML-код для отображения в окне
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyWebview Example</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f9;
            color: #333;
        }
        h1 {
            color: #4a56c6;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            color: #fff;
            background-color: #4a56c6;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #3a43a6;
        }
    </style>
</head>
<body>
    <h1>Добро пожаловать в PyWebview!</h1>
    <p>Это пример графического интерфейса, созданного с помощью PyWebview.</p>
    <button id="greetBtn">Нажмите меня</button>
    <p id="message"></p>

    <script>
        // Добавляем обработчик события для кнопки
        document.getElementById('greetBtn').addEventListener('click', function() {
            // Отправляем сообщение в Python через API
            pywebview.api.greet('Hello from JavaScript!').then(response => {
                document.getElementById('message').innerText = response;
            });
        });

        // Определяем API для взаимодействия с Python
        window.pywebview = {
            api: {
                greet: function(message) {
                    return new Promise(function(resolve, reject) {
                        resolve(`Python says: ${message}`);
                    });
                }
            }
        };
    </script>
</body>
</html>
"""

# Функция для обработки вызова из JavaScript
def greet(message):
    print(f"Получено сообщение из JavaScript: {message}")
    return f"Python получил ваше сообщение: {message}"

# Добавляем FFmpeg в PATH
ffmpeg_bin_path = str(ffmpeg_dir / "ffmpeg-7.1-essentials_build" / "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

class VideoDownloaderApp:
    def __init__(self, root):

        webview.create_window('Hello world', 'https://pywebview.flowrl.com/hello')
        webview.start()

        # Очередь загрузок
        self.download_queue = []

        # Поле ввода ссылки
        self.url_label = ttk.Label(root, text=f"Введите ссылку на видео:")
        self.url_label.pack(pady=5)

        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        self.download_audio = ttk.Checkbutton(root, text="Скачать только аудио", command=self.download_audio_check)
        self.download_audio.pack(pady=5)

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

    def download_audio_check(self):
        global audio_dl
        if audio_dl != True:
            audio_dl = True
        else:
            audio_dl = False
        print(audio_dl)
    
    def downloading_audio(self, url, output_folder):
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
    
    def downloading_video(self, url, output_folder, resolution):
        def progress_hook(d):
            if d['status'] == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)  # Избегаем деления на ноль
                progress = int((downloaded_bytes / total_bytes) * 100)
                self.update_progress(progress, f"Скачивается... {progress}%")
            elif d['status'] == 'finished':
                self.update_progress(100, "Загрузка завершена!")

        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'socket_timeout': 60,
            'progress_hooks' : [progress_hook],
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
            if audio_dl == True:
                self.downloading_audio(url, output_folder)
            else:
                self.downloading_video(url, output_folder, '1080')

        self.status_label.config(text="Статус: Все загрузки завершены!")
        self.progress['value'] = '0'

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
