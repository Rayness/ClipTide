# app/modules/converter/converter.py

import json
import os
import threading
import time
import uuid
import subprocess
import ffmpeg
# from tkinter import Tk, filedialog
from app.utils.converter_utils import get_thumbnail_base64, print_video_info
from app.modules.settings.settings import open_folder

class Converter:
    def __init__(self, context):
        self.ctx = context
        self.queue = []         # Очередь файлов
        self.is_running = False
        self.stop_requested = False
        self.current_process = None

    def _js_exec(self, code):
        if self.ctx.window:
            self.ctx.window.evaluate_js(code)

    def log(self, message):
        safe_msg = message.replace('"', '\\"').replace("'", "\\'")
        self._js_exec(f'addLog("[CONV] {safe_msg}")')

    def openFile(self):
        import webview
        # Заменяем Tkinter на pywebview
        ft =  ("Video and Audio files (*.mp4;*.avi;*.mkv;*.mov;*.mp3;*.wav)", "All files (*.*)")
        file_paths = self.ctx.window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=ft
        )
        # root.destroy()

        if not file_paths:
            return

        self._js_exec('showSpinner()')
        
        # Обрабатываем файлы в потоке, чтобы не вешать UI при генерации превью
        def _process_add():
            for path in file_paths:
                try:
                    task_id = str(uuid.uuid4())
                    filename = os.path.basename(path)
                    
                    # Пробуем получить метаданные
                    thumb, error = get_thumbnail_base64(path)
                    meta = print_video_info(path)
                    
                    # Дефолтные значения
                    duration = 0
                    bitrate = 0
                    width = "?"
                    height = "?"
                    codec = "?"
                    fps = 0
                    a_codec = "?"
                    a_bitrate = 0

                    # Распаковка метаданных (если они есть)
                    if meta and isinstance(meta, tuple) and len(meta) >= 8:
                        duration = meta[0]
                        bitrate = meta[1]
                        width = meta[2]
                        height = meta[3]
                        codec = meta[4]
                        fps = meta[5]
                        a_codec = meta[6]
                        a_bitrate = meta[7]
                    
                    item = {
                        "id": task_id,
                        "path": path,
                        "filename": filename,
                        "thumbnail": thumb,
                        "duration": duration,
                        "status": "queued",
                        "error": error,
                        # Добавляем подробности для UI
                        "details": {
                            "bitrate": bitrate,
                            "resolution": f"{width}x{height}" if width != "?" else "N/A",
                            "codec": codec,
                            "fps": fps,
                            "audio": f"{a_codec} ({a_bitrate} kbps)"
                        }
                    }
                    
                    self.queue.append(item)
                    json_item = json.dumps(item) 
                    self._js_exec(f'addConverterItem({json_item})')
                    
                except Exception as e:
                    self.log(f"Ошибка добавления {path}: {e}")
            
            self._js_exec('hideSpinner()')

        threading.Thread(target=_process_add, daemon=True).start()

    def remove_item(self, task_id):
        self.queue = [x for x in self.queue if x["id"] != task_id]
        self.log("Файл удален из очереди")

    def start_conversion(self, settings_map):
        """
        settings_map: Словарь { "task_id": {format:..., codec:...}, ... }
        Приходит из JS.
        """
        if self.is_running: return

        # 1. Обновляем настройки в очереди (в Python) данными из JS
        for item in self.queue:
            t_id = item["id"]
            if t_id in settings_map:
                item["settings"] = settings_map[t_id]
            else:
                # Фолбек, если вдруг чего-то нет (хотя не должно быть)
                item["settings"] = {
                    'format': 'mp4', 'codec': 'libx264', 
                    'quality': '23', 'resolution': 'original'
                }

        self.stop_requested = False
        self.is_running = True
        
        threading.Thread(target=self._conversion_loop, daemon=True).start()

    def stop_conversion(self):
        self.stop_requested = True
        if self.current_process:
            self.current_process.terminate()
        self.log("Остановка конвертации...")

    def _conversion_loop(self): # Убрали аргумент settings, они теперь внутри item
        self.log("Старт пакетной конвертации")
        
        out_folder = self.ctx.converter_folder
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        for item in self.queue:
            if self.stop_requested: break
            if item["status"] == "done": continue

            # === Берем индивидуальные настройки ===
            s = item.get("settings", {})
            out_fmt = s.get('format', 'mp4')
            codec = s.get('codec', 'libx264')
            crf = s.get('quality', '23')
            res = s.get('resolution', 'original')
            # ======================================

            item["status"] = "processing"
            task_id = item["id"]
            self._js_exec(f'updateConvStatus("{task_id}", "Converting...", 0)')

            try:
                base_name = os.path.splitext(item["filename"])[0]
                output_path = os.path.join(out_folder, f"conv_{base_name}.{out_fmt}")
                
                # --- Сборка команды (та же, но использует переменные выше) ---
                command = ['ffmpeg', '-y', '-i', item["path"]]
                
                if out_fmt in ['mp3', 'aac', 'wav']:
                    command.extend(['-vn'])
                    if out_fmt == 'mp3': command.extend(['-c:a', 'libmp3lame', '-q:a', '2'])
                    elif out_fmt == 'aac': command.extend(['-c:a', 'aac', '-b:a', '192k'])
                else:
                    if codec == 'copy':
                        command.extend(['-c', 'copy'])
                    else:
                        command.extend(['-c:v', codec, '-preset', 'medium', '-crf', crf])
                        command.extend(['-c:a', 'aac', '-b:a', '128k'])
                        if res != 'original':
                            command.extend(['-vf', f'scale=-2:{res}'])

                command.append(output_path)
                
                self.log(f"[{out_fmt}] {item['filename']}")
                
                self.current_process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='ignore',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                # ... (цикл чтения прогресса без изменений) ...
                duration = item.get("duration", 0)
                for line in self.current_process.stdout:
                    if "time=" in line:
                        try:
                            time_str = line.split("time=")[1].split()[0]
                            h, m, s = map(float, time_str.split(":"))
                            curr_seconds = h*3600 + m*60 + s
                            if duration > 0:
                                percent = min(round((curr_seconds / duration) * 100), 99)
                                self._js_exec(f'updateConvStatus("{task_id}", "{percent}%", {percent})')
                        except: pass
                
                self.current_process.wait()

                if self.current_process.returncode == 0:
                    item["status"] = "done"
                    self._js_exec(f'updateConvStatus("{task_id}", "Done", 100)')
                else:
                    item["status"] = "error"
                    self._js_exec(f'updateConvStatus("{task_id}", "Error", 0)')

            except Exception as e:
                self.log(f"Error: {e}")
                item["status"] = "error"
                self._js_exec(f'updateConvStatus("{task_id}", "Error", 0)')

        self.is_running = False
        self.current_process = None
        self._js_exec('conversionFinished()')
        
        open_cv = self.ctx.config.get("Folders", "cv", fallback="True")
        if open_cv == "True":
            open_folder(out_folder)