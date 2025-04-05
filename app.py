import os
import sys
import subprocess
import threading
import yt_dlp
import webview
import json
import time
from plyer import notification
import configparser
import atexit
import requests
from tkinter import Tk, filedialog
from pathlib import Path
import re
from concurrent.futures import ThreadPoolExecutor

class DownloadTask:
    def __init__(self, task_id, url, title, format, resolution, thumbnail):
        self.task_id = task_id
        self.url = url
        self.title = title
        self.format = format
        self.resolution = resolution
        self.thumbnail = thumbnail
        self.status = "queued"
        self.progress = 0
        self.speed = "0 KB/s"
        self.cancelled = False

class Api:
    def __init__(self):
        self.download_queue = []
        self.active_downloads = {}
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.download_tasks = {}
        self.download_folder = str(Path.home() / 'Downloads' / 'ClipTide')
        
    def remove_emoji(self, text):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)

    def add_video_to_queue(self, video_url, selected_format, selected_resolution):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title = self.remove_emoji(info.get('title', 'Unknown video')).replace('"', "'")
                thumbnail = info.get('thumbnail', '')
            
            task_id = f"task_{int(time.time())}"
            task = DownloadTask(
                task_id=task_id,
                url=video_url,
                title=video_title,
                format=selected_format,
                resolution=selected_resolution,
                thumbnail=thumbnail
            )
            
            self.download_queue.append(task)
            self.download_tasks[task_id] = task
            
            # Обновляем интерфейс
            window.evaluate_js(f"""
                addVideoToList(
                    "{task_id}",
                    "{video_title}",
                    "{thumbnail}",
                    "{selected_format}",
                    "{selected_resolution}"
                )
            """)
            
            return f"Added to queue: {video_title}"
            
        except Exception as e:
            return f"Error: {str(e)}"

    def start_download(self):
        if len(self.active_downloads) >= 3:
            return "Maximum parallel downloads reached"
        
        if not self.download_queue:
            return "Queue is empty"
        
        # Запускаем доступные загрузки
        while len(self.active_downloads) < 3 and self.download_queue:
            task = self.download_queue.pop(0)
            future = self.executor.submit(self.download_video, task)
            self.active_downloads[task.task_id] = future
            
        return "Download started"

    def download_video(self, task):
        try:
            task.status = "downloading"
            window.evaluate_js(f'updateTaskStatus("{task.task_id}", "downloading")')
            
            ydl_opts = {
                'outtmpl': f'{self.download_folder}/%(title)s.%(ext)s',
                'progress_hooks': [lambda d: self.progress_hook(d, task.task_id)],
                'retries': 3,
                'socket_timeout': 30,
            }
            
            if task.format != 'mp3':
                ydl_opts['format'] = f'bestvideo[height<={task.resolution}]+bestaudio/best'
                ydl_opts['merge_output_format'] = task.format
            else:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([task.url])
                
            if not task.cancelled:
                task.status = "completed"
                window.evaluate_js(f'updateTaskStatus("{task.task_id}", "completed")')
                notification.notify(
                    title='Download complete',
                    message=f'Finished: {task.title}',
                    timeout=5
                )
                
        except Exception as e:
            if not task.cancelled:
                task.status = "error"
                window.evaluate_js(f'updateTaskStatus("{task.task_id}", "error")')
                
        finally:
            # Удаляем из активных загрузок
            if task.task_id in self.active_downloads:
                del self.active_downloads[task.task_id]
            
            # Запускаем следующую загрузку, если есть очередь
            self.start_download()

    def progress_hook(self, d, task_id):
        if d['status'] == 'downloading':
            task = self.download_tasks.get(task_id)
            if not task or task.cancelled:
                return
                
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
            speed = d.get('speed', 0)
            
            task.progress = (downloaded / total) * 100
            task.speed = f"{speed / (1024 * 1024):.2f} MB/s"
            
            window.evaluate_js(f"""
                updateTaskProgress(
                    "{task_id}",
                    {task.progress},
                    "{task.speed}"
                )
            """)
            
    def cancel_download(self, task_id):
        task = self.download_tasks.get(task_id)
        if task and task.status == "downloading":
            task.cancelled = True
            task.status = "cancelled"
            window.evaluate_js(f'updateTaskStatus("{task_id}", "cancelled")')
            return True
        return False

    def remove_task(self, task_id):
        task = self.download_tasks.get(task_id)
        if task:
            if task.status == "downloading":
                self.cancel_download(task_id)
            self.download_queue = [t for t in self.download_queue if t.task_id != task_id]
            if task_id in self.download_tasks:
                del self.download_tasks[task_id]
            return True
        return False

if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        'ClipTide',
        'data/ui/new/index.html',
        js_api=api,
        width=1200,
        height=800,
        resizable=True
    )
    
    def on_exit():
        print("Saving queue before exit...")
        
    atexit.register(on_exit)
    webview.start()