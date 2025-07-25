# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import os
import json
import ffmpeg
import subprocess
import time
from threading import Thread
from tkinter import Tk, filedialog
from app.utils.converter_utils import get_thumbnail_base64, print_video_info
from app.modules.settings import open_folder

class Converter():
    def __init__(self, window, translations, output_path, notifications, notification, open_folders):
        self.window = window
        self.translations = translations
        self.notifications = notifications
        self.convert_video_path = None
        self.output_path = output_path
        self.notification = notification
        self.open_folder = open_folders

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
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('converter', {}).get('video_adding')}"')
            self.window.evaluate_js(f'showSpinner()')
            self.window.evaluate_js(f'window.updateTranslations({self.translations})')
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
            self.window.evaluate_js(f"file_is_input({json.dumps(video_data)})")
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('converter', {}).get('video_add')}"')
            time.sleep(2)
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')
        except Exception as e:
            print("Ошибка при выборе видео")
            self.window.evaluate_js(f'hideSpinner()')
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get('status', {}).get('status_text')}"')

    # Функция для конвертации видео
    def convert_video(self, output_format):
        try:
            filename = os.path.splitext(os.path.basename(self.convert_video_path))[0]
            output_path = os.path.join(self.output_path, f"{filename}.{output_format}")

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
                            self.window.evaluate_js(f'showSpinner()')
                            self.window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} {progress}%"')
                            self.window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} {eta_formatted}"')
                            self.window.evaluate_js(f'document.getElementById("progress-fill").style.width = "{progress}%"')
                        except Exception as e:
                            print(f"Ошибка при обработке строки: {line.strip()}. Подробности: {str(e)}")
                            continue

                self.ffmpeg_process.wait()
                if progress > 99:
                    # Уведомляем об успешной конвертации
                    self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("convert_success")}"')
                    self.window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} 100%"')
                    time.sleep(2)
                    open_folder(self.output_path)
                    self.window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} 0%"')
                    self.window.evaluate_js(f'closeVideo()')
                    self.window.evaluate_js(f'hideSpinner()')
                    self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("status_text")}"')
                    self.window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} 0 мин 0 сек"')
                    self.window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')

            # Запускаем процесс конвертации в отдельном потоке
            ffmpeg_thread = Thread(target=run_ffmpeg)
            ffmpeg_thread.start()

            # Уведомляем о начале конвертации
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("converting")}"')

            # Ждем завершения потока
            ffmpeg_thread.join()
        except Exception as e:
            print(f"Ошибка при конвертации: {str(e)}")
            self.window.evaluate_js(f'hideSpinner()')
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("convert_error")}: {str(e)}"')
            time.sleep(2)
            self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("status_text")}"')


    def stop_conversion(self):
        # Прерывает процесс конвертации
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:  # Проверяем, что процесс еще работает
            try:
                self.ffmpeg_process.terminate()  # Отправляем сигнал завершения
                print("Конвертация прервана пользователем.")
                self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("conversion_stopped")}"')
                time.sleep(2)
                self.window.evaluate_js(f'hideSpinner()')
                self.window.evaluate_js(f'document.getElementById("status").innerText = "{self.translations.get("status", {}).get("status_text")}"')
                self.window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} 0 мин 0 сек"')
                self.window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translations['progress']} 0%"')
                self.window.evaluate_js(f'document.getElementById("progress-fill").style.width = "0%"')
            except Exception as e:
                print(f"Ошибка при попытке прервать конвертацию: {str(e)}")