# app/modules/converter/converter.py

import os
import json
import ffmpeg
import subprocess
import time
from threading import Thread
from tkinter import Tk, filedialog
from app.utils.converter_utils import get_thumbnail_base64, print_video_info
from app.modules.settings.settings import open_folder

class Converter:
    def __init__(self, context):
        self.ctx = context
        self.convert_video_path = None
        self.ffmpeg_process = None

    def openFile(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=(("Video files", "*.mp4;*.avi;*.mkv;*.mov"), ("All files", "*.*"))
        )
        root.destroy()

        if not file_path:
            return

        try:
            self.ctx.log_status('converter', 'video_adding') # Используем ключи из json
            self.ctx.js_exec('showSpinner()')

            thumbnail, error = get_thumbnail_base64(file_path)
            result = print_video_info(file_path)
            
            # Дефолтные значения
            video_data = {
                'file_name': os.path.basename(file_path),
                'thumbnail': thumbnail,
                'error': error
            }

            if result and len(result) == 8:
                video_data.update({
                    'duration': result[0], 'bitrate': result[1],
                    'width': result[2], 'height': result[3],
                    'codec': result[4], 'fps': result[5],
                    'audio_codec': result[6], 'audio_bitrate': result[7]
                })

            self.convert_video_path = file_path
            
            # Обновляем UI
            self.ctx.js_exec(f"file_is_input({json.dumps(video_data)})")
            self.ctx.log_status('converter', 'video_add')
            time.sleep(1)
            self.ctx.log_status('status_text') # Сброс статуса

        except Exception as e:
            print(f"Converter Error: {e}")
            self.ctx.js_exec('hideSpinner()')
            self.ctx.log_status('error_adding', str(e))

    def convert_video(self, output_format):
        if not self.convert_video_path:
            return

        out_folder = self.ctx.converter_folder
        filename = os.path.splitext(os.path.basename(self.convert_video_path))[0]
        output_path = os.path.join(out_folder, f"{filename}.{output_format}")

        self.ctx.log_status('converting')

        # Запускаем поток
        Thread(target=self._run_ffmpeg, args=(output_path,)).start()

    def _run_ffmpeg(self, output_path):
        try:
            # Получаем длительность для расчета прогресса
            probe = ffmpeg.probe(self.convert_video_path)
            duration = float(probe['format']['duration'])

            command = [
                'ffmpeg', '-i', self.convert_video_path,
                '-c:v', 'libx264', '-preset', 'medium',
                '-c:a', 'aac', '-y', output_path
            ]

            self.ffmpeg_process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, encoding='utf-8', errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for line in self.ffmpeg_process.stdout:
                if "time=" in line:
                    self._parse_progress(line, duration)

            self.ffmpeg_process.wait()

            if self.ffmpeg_process.returncode == 0:
                self.ctx.log_status('convert_success')
                self.ctx.js_exec(f'document.getElementById("progress").innerText = "100%"')
                self.ctx.js_exec(f'document.getElementById("progress-fill").style.width = "100%"')
                
                # Проверяем настройки автооткрытия папки
                if self.ctx.config.get("Folders", "cv", fallback="True") == "True":
                    open_folder(os.path.dirname(output_path))
                
                time.sleep(2)
                # Сброс UI
                self.ctx.js_exec('closeVideo()')
                self.ctx.js_exec('hideSpinner()')
                self.ctx.log_status('status_text')
                self._reset_progress_ui()

        except Exception as e:
            print(f"FFmpeg Error: {e}")
            self.ctx.log_status('convert_error', str(e))
            self.ctx.js_exec('hideSpinner()')

    def _parse_progress(self, line, duration):
        try:
            time_str = line.split("time=")[1].split()[0]
            if time_str == 'N/A': return
            
            h, m, s = map(float, time_str.split(":"))
            current_time = h * 3600 + m * 60 + s
            
            progress = min(round((current_time / duration) * 100, 2), 100)
            
            # Отправляем в UI
            self.ctx.js_exec(f'updateProgressBar({progress}, "", "")') # Нужно адаптировать JS функцию
            # Или по-старому:
            self.ctx.js_exec(f'document.getElementById("progress").innerText = "{progress}%"')
            self.ctx.js_exec(f'document.getElementById("progress-fill").style.width = "{progress}%"')
            
        except:
            pass

    def _reset_progress_ui(self):
        self.ctx.js_exec('document.getElementById("progress").innerText = "0%"')
        self.ctx.js_exec('document.getElementById("eta").innerText = ""')
        self.ctx.js_exec('document.getElementById("progress-fill").style.width = "0%"')

    def stop_conversion(self):
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            self.ffmpeg_process.terminate()
            self.ctx.log_status('conversion_stopped')
            self._reset_progress_ui()
            self.ctx.js_exec('hideSpinner()')