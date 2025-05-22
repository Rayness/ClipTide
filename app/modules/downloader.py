import os
import threading
import time

import yt_dlp

from app.utils.const import COOKIES_FILE
from app.utils.queue import save_queue_to_file

class Downloader():
    def __init__(self, window, translations, download_queue, download_folder):
        self.window = window
        self.translations = translations
        self.download_queue = download_queue
        self.download_folder = download_folder
        self.is_downloading = False
        self.download_stop = False
        print("Перевод в загрузчике: ", translations)
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
            self.window.evaluate_js(f'removeVideoFromList("{video_title}")')
            
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('removed_from_queue')}: {video_title}"'), time.sleep(3), self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            time.sleep(2)
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
        except Exception as e:
            print(f"Ошибка при удалении видео из очереди: {str(e)}", video_title)
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('error_removing')}: {str(e)}"'), time.sleep(3), self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            time.sleep(2)
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')

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
            self.window.evaluate_js(f'addVideoToList("{video_title}", "{thumbnail_url}", "{selected_format}","{selectedResolution}")')
            
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('to_queue')}: {video_title} {self.translations.get('status', {}).get('in_format')} {selected_format} {self.translations.get('status', {}).get('in_resolution')} {selectedResolution}p"')
            self.window.evaluate_js(f'hideSpinner()')
            time.sleep(3)
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            return
        except Exception as e:
            print(f"Ошибка при добавлении видео в очередь: {str(e)}")
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('error_adding')}: {str(e)}"')
            self.window.evaluate_js(f'hideSpinner()')
            time.sleep(3)
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
            return 
        
    # Функция для начала загрузки
    def startDownload(self):
        if self.is_downloading: 
            return f"{self.translations.get('status', {}).get('downloading_already')}"

        if not self.download_queue:
            return f"{self.translations.get('status', {}).get('the_queue_is_empty')}"
        
        # Запускаем загрузку
        self.start_next_download()
        self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('downloading')}: {video_title}"') # type: ignore
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
                    self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('the_queue_is_empty_download_success')}"')
                    time.sleep(3)
                    self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
                    return

                # Устанавливаем флаг загрузки
                self.is_downloading = True

                save_queue_to_file(self.download_queue)

                # Извлекаем следующее видео из очереди
                video_url, video_title, selected_format, selectedResolution, thumbl = self.download_queue.pop(0)
                print(f"Начинаю загрузку видео: {video_title} в формате {selected_format} в разрешении {selectedResolution}p")
                self.window.evaluate_js(f'showSpinner()')

                # Обновляем статус в интерфейсе
                self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('downloading')}: {video_title}"')
                self.window.evaluate_js(f'removeVideoFromList("{video_title}")')

                # Запускаем загрузку видео
                threading.Thread(target=self.download_video, args=(video_url, video_title, selected_format, selectedResolution, self.download_folder)).start()

                print("Очередь пуста")
            else:
                save_queue_to_file(self.download_queue)
                self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
                self.window.evaluate_js('hideSpinner()')
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
            self.window.evaluate_js(f'hideSpinner()')
            print(f"Видео успешно загружено: {video_title}")
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('download_success')}: {video_title}"')
        except Exception as e:
            print(f"Ошибка при загрузке: {str(e)}")
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('download_error')}: {str(e)}"')
            self.window.evaluate_js(f'hideSpinner()')
            time.sleep(3)
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')

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
                self.window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} {progress}%"')
                self.window.evaluate_js(f'document.getElementById("speed").innerText = "{self.translations['speed']} {speed_formatted}"')
                self.window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} {eta_formatted}"')
                self.window.evaluate_js(f'document.getElementById("progress-fill").style.width = "{progress}%"')
            elif d['status'] == 'finished':
                # Загрузка завершена
                self.window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} 100%"')
                self.window.evaluate_js(f'document.getElementById("speed").innerText = "{self.translations['speed']} 0"')
                self.window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} 0"')
                self.window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')
        else:
            # Загрузка отменена
            self.window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} 0%"')
            self.window.evaluate_js(f'document.getElementById("speed").innerText = "{self.translations['speed']} 0"')
            self.window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} 0"')
            self.window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')
            raise yt_dlp.utils.DownloadCancelled("Загрузка отменена")