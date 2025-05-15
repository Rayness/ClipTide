# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import subprocess
import threading
from threading import Thread
import time
import json
import ffmpeg
import yt_dlp
import os
from tkinter import Tk, filedialog
from utils.translations import load_translations 
from utils.config import load_config, save_config
from utils.const import COOKIES_FILE, UPDATER, html_file_path, download_dir
from utils.queue import load_queue_from_file, save_queue_to_file
from utils.converter_utils import get_thumbnail_base64, print_video_info
from utils.ui import createwindow
from utils.utils import check_for_update

config = load_config()

class Api():
    def __init__(self):
        self.download_queue = load_queue_from_file()
        self.download_folder = ''
        self.is_downloading = False  # Флаг для отслеживания состояния загрузки
        self.convert_video_path = ''
        self.ffmpeg_process = None
        self.download_thread = None
        self.download_stop = False
        self.translations = "ru"

    # Запуск программы обновления
    def launch_update(self):
        try:
            result = subprocess.run(["powershell", "Start-Process", UPDATER, "-Verb", "runAs"], shell=True)
            print("Код завершения:", result.returncode)
            print("Вывод программы:", result.stdout.decode())
            return result
        except Exception as e:
            print("Ошибки:", result.stderr.decode())
            print(f"Ошибка при запуске апдейтера: {str(e)}")
    
    # функция для выбора видео для конвертации
    def openFile(self):
        # Открытие диалогового окна для выбора папки
        root = Tk()
        root.withdraw()  # Скрываем главное окно tkinter
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл",
                filetypes=(("Все файлы", "*.*"), ("Текстовые файлы", "*.txt"), ("Видео", "*.mp4;*.avi"))
            )
        except Exception as e:
            print(f"Ошибка при выборе папки: {e}")
        root.destroy()
        try:
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('converter', {}).get('video_adding')}"')
            window.evaluate_js(f'showSpinner()')
            thumbnail, error = get_thumbnail_base64(file_path)
            result = print_video_info(file_path)
            if result is None:
                print("Не удалось получить данные о видео")
            else:
                if result and len(result) == 8:
                    duration, bitrate, width, height, codec, fps, audio_codec, audio_bitrate = result
                else: 
                    print(result)
            file_name = os.path.basename(file_path)
            self.convert_video_path = file_path
            # print(duration, bitrate, codec, fps, audio_codec, audio_bitrate, thumbnail, error, file_name)

            # Формируем данные
            video_data = {
                'duration': duration,
                'bitrate': bitrate,
                'codec': codec,
                'fps': fps,
                'audio_codec': audio_codec,
                'audio_bitrate': audio_bitrate,
                'thumbnail': thumbnail,
                'error': error,
                'file_name': file_name
            }
            window.evaluate_js(f"file_is_input({json.dumps(video_data)})")
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('converter', {}).get('video_add')}"')
            time.sleep(2)
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
        except Exception as e:
            print("Ошибка при выборе видео")
            window.evaluate_js(f'hideSpinner()')
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            

    # Функция для смены языка
    def switch_language(self, language):
        self.current_language = language
        self.translations = load_translations(language)
        config.set("Settings", "language", self.current_language)
        save_config(config)
        window.evaluate_js(f'window.updateTranslations({json.dumps(self.translations)})')

    # Функция для смены папки загрузок
    def switch_download_folder(self, folder_path=f'{download_dir}'):
        self.current_folder = folder_path if folder_path is not None else download_dir
        config.set("Settings", "folder_path", self.current_folder)
        save_config(config)
        self.download_folder = self.current_folder
        print("Folder_path: " + folder_path, "download_folder: " + self.download_folder)
        window.evaluate_js(f'updateDownloadFolder({json.dumps(self.current_folder)})')

    # Функция для выбора папки для загрузки
    def choose_folder(self):
        # Открытие диалогового окна для выбора папки
        root = Tk()
        root.withdraw()  # Скрываем главное окно tkinter
        try:
            folder_path = filedialog.askdirectory()  # Открывает окно выбора папки
            window.evaluate_js(f'updateDownloadFolder({json.dumps(folder_path)})')
            self.switch_download_folder(folder_path)
        except Exception as e:
            print(f"Ошибка при выборе папки: {e}")
        root.destroy()

    # Функция для открытия папки с загрузками
    def open_folder(self):
        try:
            os.startfile(f"{self.download_folder}")
        except Exception as e:
            print(f"Ошибка: {e}")

    # Функция для конвертации видео
    def convert_video(self, output_format):
        try:
            filename = os.path.splitext(os.path.basename(self.convert_video_path))[0]
            output_path = os.path.join(self.download_folder, f"{filename}.{output_format}")

            print(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("converting")}"')
                

            # Получаем длительность видео
            probe = ffmpeg.probe(self.convert_video_path)
            duration = float(probe['format']['duration'])
            # Команда ffmpeg
            command = [
                'ffmpeg',
                '-i', self.convert_video_path,
                '-c:v', 'libx264',  # Пример кодека видео
                '-preset', 'medium',  # Скорость/качество конвертации
                '-c:a', 'aac',  # Пример кодека аудио
                output_path
            ]
           # Запускаем процесс FFmpeg в отдельном потоке
            def run_ffmpeg():
                self.ffmpeg_process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='ignore',  # Явно указываем кодировку UTF-8
                    creationflags=subprocess.CREATE_NO_WINDOW  # Предотвращает открытие консоли
                )
                # Чтение вывода FFmpeg для анализа прогресса
                for line in self.ffmpeg_process.stdout:
                    print(line.strip())  # Для отладки
                    if "time=" in line:
                        try:
                            # Извлекаем текущее время обработки из строки
                            time_str = line.split("time=")[1].split()[0]
                            if time_str == 'N/A':
                                continue
                            hours, minutes, seconds = map(float, time_str.split(":"))
                            current_time = hours * 3600 + minutes * 60 + seconds

                            # Вычисляем процент завершения
                            progress = (current_time / duration) * 100 if duration > 0 else 0
                            progress = min(progress, 100)  # Ограничиваем значение до 100%
                            progress = round(progress, 2)

                            eta_seconds_total = max(duration - current_time, 0)
                            eta_minutes = int(eta_seconds_total // 60)
                            eta_seconds = int(eta_seconds_total % 60)

                            eta_formatted = f"{eta_minutes} {self.translations['min']} {eta_seconds} {self.translations['sec']}"

                            # Обновляем прогресс-бар в интерфейсе
                            window.evaluate_js(f'showSpinner()')
                            window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} {progress}%"')
                            window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} {eta_formatted}"')
                            window.evaluate_js(f'document.getElementById("progress-fill").style.width = "{progress}%"')
                        except Exception as e:
                            print(f"Ошибка при обработке строки: {line.strip()}. Подробности: {str(e)}")
                            continue

                self.ffmpeg_process.wait()
                if progress > 99:
                    # Уведомляем об успешной конвертации
                    window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("convert_success")}"')
                    window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} 100%"')
                    time.sleep(2)
                    self.open_folder()
                    window.evaluate_js(f'closeVideo()')
                    window.evaluate_js(f'hideSpinner()')
                    window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("status_text")}"')
                    window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} 0 мин 0 сек"')
                    window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')

            # Запускаем процесс конвертации в отдельном потоке
            ffmpeg_thread = Thread(target=run_ffmpeg)
            ffmpeg_thread.start()

            # Уведомляем о начале конвертации
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("converting")}"')

            # Ждем завершения потока
            ffmpeg_thread.join()
        except Exception as e:
            print(f"Ошибка при конвертации: {str(e)}")
            window.evaluate_js(f'hideSpinner()')
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("convert_error")}: {str(e)}"')
            time.sleep(2)
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("status_text")}"')


    def stop_conversion(self):
        # Прерывает процесс конвертации
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:  # Проверяем, что процесс еще работает
            try:
                self.ffmpeg_process.terminate()  # Отправляем сигнал завершения
                print("Конвертация прервана пользователем.")
                window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("conversion_stopped")}"')
                time.sleep(2)
                window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            except Exception as e:
                print(f"Ошибка при попытке прервать конвертацию: {str(e)}")

    # Функция для удаления видео из очереди
    def removeVideoFromQueue(self, video_title):
        try:
            # Фильтруем очередь, удаляя видео с указанным названием
            self.download_queue = [
                (url, title, fmt, res, thumb)
                for url, title, fmt, res, thumb in self.download_queue
                if title != video_title
            ]

            # Сохраняем обновленную очередь в файл
            save_queue_to_file(self.download_queue)

            print(f"Видео удалено из очереди: {video_title}")
            print(video_title)
            # Обновляем интерфейс
            window.evaluate_js(f'removeVideoFromList("{video_title}")')
            
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('removed_from_queue')}: {video_title}"'), time.sleep(3), window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            time.sleep(2)
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
        except Exception as e:
            print(f"Ошибка при удалении видео из очереди: {str(e)}", video_title)
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('error_removing')}: {str(e)}"'), time.sleep(3), window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            time.sleep(2)
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')

    # Функция для добавления видео в очередь
    def addVideoToQueue(self, video_url, selected_format, selectedResolution):
        try:
            # Извлекаем информацию о видео (название)
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title_get = info.get('title', 'Неизвестное видео')
                thumbnail_url = info.get('thumbnail', '')
            # video_title = self.remove_emoji_simple(video_title_get.replace('"',"'"))
            video_title = video_title_get.replace('"',"'")


            # Добавляем видео в очередь
            self.download_queue.append((video_url, video_title, selected_format, selectedResolution, thumbnail_url))
            print(f"Видео добавлено в очередь: {video_title} в формате {selected_format} в разрешении {selectedResolution}p")

            # Сохраняем очередь в файл
            save_queue_to_file(self.download_queue)

            # Обновляем интерфейс
            window.evaluate_js(f'addVideoToList("{video_title}", "{thumbnail_url}", "{selected_format}","{selectedResolution}")')
            
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('to_queue')}: {video_title} {self.translations.get('status', {}).get('in_format')} {selected_format} {self.translations.get('status', {}).get('in_resolution')} {selectedResolution}p"')
            window.evaluate_js(f'hideSpinner()')
            time.sleep(3)
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            return
        except Exception as e:
            print(f"Ошибка при добавлении видео в очередь: {str(e)}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('error_adding')}: {str(e)}"')
            window.evaluate_js(f'hideSpinner()')
            time.sleep(3)
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            return 
        
    # Функция для начала загрузки
    def startDownload(self):
        if self.is_downloading: 
            return f"{self.translations.get('status', {}).get('downloading_already')}"

        if not self.download_queue:
            return f"{self.translations.get('status', {}).get('the_queue_is_empty')}"
        
        # Запускаем загрузку
        self.start_next_download()
        window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('downloading')}: {video_title}"') # type: ignore
        return
    
    def stopDownload(self):
        self.is_downloading = False
        self.download_stop = True
        print(self.download_stop)

    # Функция для начала следующей загрузки
    def start_next_download(self):
            if not self.download_stop:
                if not self.download_queue:
                    os.startfile(f"{self.download_folder}")
                    print("Очередь пуста. Загрузка завершена.")
                    # Обновляем статус
                    window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('the_queue_is_empty_download_success')}"')
                    time.sleep(3)
                    window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
                    return

                # Устанавливаем флаг загрузки
                self.is_downloading = True

                save_queue_to_file(self.download_queue)

                # Извлекаем следующее видео из очереди
                video_url, video_title, selected_format, selectedResolution, thumbl = self.download_queue.pop(0)
                print(f"Начинаю загрузку видео: {video_title} в формате {selected_format} в разрешении {selectedResolution}p")
                window.evaluate_js(f'showSpinner()')

                # Обновляем статус в интерфейсе
                window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('downloading')}: {video_title}"')
                window.evaluate_js(f'removeVideoFromList("{video_title}")')

                # Запускаем загрузку видео
                threading.Thread(target=self.download_video, args=(video_url, video_title, selected_format, selectedResolution, self.download_folder)).start()

                print("Очередь пуста")
            else:
                save_queue_to_file(self.download_queue)
                window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
                window.evaluate_js('hideSpinner()')
                self.download_stop = False
    # Функция для загрузки видео с помощью yt-dlp
    def download_video(self, video_url, video_title, selected_format, selectedResolution, download_folder='downloads'):
        try:
            if (selected_format != 'mp3'):
                # Настройки для yt-dlp
                ydl_opts = {
                    'format': f'bestvideo[height<={selectedResolution}]+bestaudio/best[height<={selectedResolution}]',  # Лучшее качество видео и аудио
                    'merge_output_format': selected_format,  # Объединяем видео и аудио в один файл
                    'outtmpl': f'{download_folder}/{video_title}.{selected_format}',  # Путь для сохранения
                    'progress_hooks': [self.progress_hook],  # Добавляем хук для отслеживания прогресса
                    'cookiefile': f'{COOKIES_FILE}',
                    'retries': 25,  # Увеличиваем количество попыток
                    'socket_timeout': 5,  # Устанавливаем таймаут для сокета
                    'nocheckcertificate': True,  # Отключаем проверку SSL-сертификата
                }
            else:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': f'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': f'{download_folder}/%(title)s.{selected_format}',  # Путь для сохранения
                    'progress_hooks': [self.progress_hook],  # Добавляем хук для отслеживания прогресса
                    'retries': 25,  # Увеличиваем количество попыток
                    'socket_timeout': 5,  # Устанавливаем таймаут для сокета
                    'nocheckcertificate': True,  # Отключаем проверку SSL-сертификата
                }


            # Загружаем видео
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            self.removeVideoFromQueue(video_title)
            window.evaluate_js(f'hideSpinner()')
            print(f"Видео успешно загружено: {video_title}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('download_success')}: {video_title}"')
        except Exception as e:
            print(f"Ошибка при загрузке: {str(e)}")
            window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('download_error')}: {str(e)}"')

        # Сбрасываем флаг загрузки и запускаем следующую загрузку
        self.is_downloading = False
        self.start_next_download()

    # Хук для отслеживания прогресса
    def progress_hook(self, d):
        if self.is_downloading == True:
            if d['status'] == 'downloading':
                # Получаем данные о прогрессе
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 1)  # Избегаем деления на ноль
                speed = d.get('speed', 0)  # Скорость в байтах/сек
                eta = d.get('eta', 0)  # Оставшееся время в секундах

                # Вычисляем прогресс
                progress = (downloaded_bytes / total_bytes) * 100 if total_bytes > 0 else 0
                progress = round(progress, 2)  # Округляем до двух знаков после запятой

                # Преобразуем ETA в читаемый формат
                eta_minutes = eta // 60 if eta is not None else 0
                eta_seconds = eta % 60 if eta is not None else 0
                eta_formatted = "Завершение загрузки..." if eta == 0 else f"{int(eta_minutes)} {self.translations['min']} {int(eta_seconds)} {self.translations['sec']}"

    # Преобразуем скорость в Мбайты/сек
                speed_mbps = speed / (1024 * 1024) if speed else 0
                speed_formatted = f"{speed_mbps:.2f} {self.translations['mbs']}"  # Форматируем до двух знаков после запятой

                # Выводим отладочную информацию
                print(f"Progress: {progress}%, Speed: {speed_formatted}, ETA: {eta_formatted}")

                # Обновляем интерфейс
                window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} {progress}%"')
                window.evaluate_js(f'document.getElementById("speed").innerText = "{self.translations['speed']} {speed_formatted}"')
                window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} {eta_formatted}"')
                window.evaluate_js(f'document.getElementById("progress-fill").style.width = "{progress}%"')
            elif d['status'] == 'finished':
                # Загрузка завершена
                window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} 100%"')
                window.evaluate_js(f'document.getElementById("speed").innerText = "{self.translations['speed']} 0B/s"')
                window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} 0 мин 0 сек"')
                window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')
        else:
            # Загрузка отменена
            window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} 100%"')
            window.evaluate_js(f'document.getElementById("speed").innerText = "{self.translations['speed']} 0B/s"')
            window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} 0 мин 0 сек"')
            window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')
            raise yt_dlp.utils.DownloadCancelled("Загрузка отменена")
  
api = Api()
window = createwindow(html_file_path, api)

def startApp():
    update = check_for_update()
    update_js = str(update).lower()

    config = load_config()
    language = config.get("Settings", "language", fallback="ru")
    download_folder = config.get("Settings", "folder_path", fallback="downloads")
    auto_update = config.getboolean("Settings", "auto_update", fallback=False)
    translations = load_translations(language)
    print(config, translations, language)

    api.translations = translations

        # Загружаем параметры при запуске
    window.events.loaded += lambda: window.evaluate_js(f'updateDownloadFolder({json.dumps(download_folder)})')
    window.events.loaded += lambda: window.evaluate_js(f'updateTranslations({json.dumps(translations)})')
    window.events.loaded += lambda: window.evaluate_js(f'window.loadQueue({json.dumps(download_queue)})')
    window.events.loaded += lambda: window.evaluate_js(f'updateApp({update_js}, {json.dumps(translations)})')

    api.download_folder = download_folder
    download_queue = api.download_queue