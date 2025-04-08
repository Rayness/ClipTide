import os
import json
import logging
import threading
import time
from datetime import datetime
import webview
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from pathlib import Path

class VideoDownloader:
    def __init__(self):
        self.download_queue = []
        self.active_downloads = {}
        self.max_parallel_downloads = 3
        self.download_folder = str(Path.home() / "Downloads")
        self.language = "en"
        self.ffmpeg_path = os.path.join("ffmpeg-7.1-essentials_build", "bin", "ffmpeg.exe")
        self.load_settings()
        self.setup_logging()
        
    def setup_logging(self):
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        log_file = os.path.join(logs_dir, f"downloads_{datetime.now().strftime('%Y%m%d')}.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.download_folder = settings.get("download_folder", self.download_folder)
                self.language = settings.get("language", self.language)
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_settings()
            
    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump({
                "download_folder": self.download_folder,
                "language": self.language
            }, f)
    
    def get_translation(self, key):
        try:
            lang_file = f"{self.language}.json"
            with open(lang_file, "r", encoding="utf-8") as f:
                translations = json.load(f)
                
            keys = key.split(".")
            result = translations
            for k in keys:
                result = result.get(k, {})
                
            return result if isinstance(result, str) else key
        except (FileNotFoundError, json.JSONDecodeError, AttributeError):
            return key
    
    def get_video_info(self, url):
        try:
            window.evaluate_js(f"showNotification('{self.get_translation('status.downloading')} {url}', 'info')")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    videos = []
                    for entry in info['entries']:
                        if entry:
                            video_info = self._extract_single_video_info(entry['url'])
                            if video_info:
                                videos.append(video_info)
                    return videos
                else:
                    return [self._extract_single_video_info(url)]
                    
        except DownloadError as e:
            error_msg = f"{self.get_translation('status.error_adding')}: {str(e)}"
            window.evaluate_js(f"showNotification('{error_msg}', 'error')")
            logging.error(f"Error getting video info: {str(e)}")
            return None
            
    def _extract_single_video_info(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                formats = []
                resolutions = set()
                has_audio_only = False
                
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        resolution = f.get('height', 0)
                        if resolution:
                            resolutions.add(resolution)
                            formats.append({
                                'format_id': f['format_id'],
                                'ext': f['ext'],
                                'resolution': resolution,
                                'note': f.get('format_note', '')
                            })
                    elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        has_audio_only = True
                
                thumbnail = info.get('thumbnail', '')
                if not thumbnail and 'thumbnails' in info:
                    thumbnail = info['thumbnails'][-1]['url']
                
                return {
                    'id': info['id'],
                    'title': info['title'],
                    'url': url,
                    'duration': info.get('duration', 0),
                    'thumbnail': thumbnail,
                    'formats': sorted(formats, key=lambda x: x['resolution'], reverse=True),
                    'resolutions': sorted(resolutions, reverse=True),
                    'has_audio_only': has_audio_only,
                    'webpage_url': info.get('webpage_url', url),
                    'extractor': info.get('extractor', 'unknown')
                }
                
        except Exception as e:
            logging.error(f"Error extracting video info: {str(e)}")
            return None
    
    def add_to_queue(self, url, format_type, resolution, download_thumbnail=False, download_subtitles=False):
        window.evaluate_js("showNotification('Getting video info...', 'info')")
        
        video_info = self.get_video_info(url)
        if not video_info:
            return False, self.get_translation("status.error_adding")
        
        for video in video_info:
            task_id = f"{video['id']}_{int(time.time())}"
            self.download_queue.append({
                'id': task_id,
                'video_info': video,
                'format': format_type,
                'resolution': resolution,
                'download_thumbnail': download_thumbnail,
                'download_subtitles': download_subtitles,
                'status': 'queued',
                'progress': 0,
                'speed': '0 KB/s',
                'eta': '--:--',
                'started_at': None,
                'completed_at': None
            })
            
            # Создаем безопасную JSON-строку для передачи в JS
            task_data = {
                'id': task_id,
                'title': video['title'],
                'extractor': video['extractor'],
                'format': format_type,
                'resolution': resolution,
                'thumbnail': video['thumbnail'],
                'status': 'queued',
                'progress': 0,
                'speed': '0 KB/s',
                'eta': '--:--'
            }
        
        # Экранируем специальные символы
        import json
        task_json = json.dumps(task_data)
        window.evaluate_js(f"addTaskToList({task_json})")
    
        return True, self.get_translation("status.to_queue")
    
    def start_download(self, task_id=None):
        if task_id:
            task = next((t for t in self.download_queue if t['id'] == task_id), None)
            if task and task['status'] == 'queued':
                self._start_single_download(task)
        else:
            queued_tasks = [t for t in self.download_queue if t['status'] == 'queued']
            active_count = len([t for t in self.download_queue if t['status'] == 'downloading'])
            
            for task in queued_tasks[:self.max_parallel_downloads - active_count]:
                self._start_single_download(task)
    
    def _start_single_download(self, task):
        if len(self.active_downloads) >= self.max_parallel_downloads:
            return
            
        task['status'] = 'downloading'
        task['started_at'] = datetime.now().isoformat()
        
        thread = threading.Thread(target=self._download_video, args=(task,))
        thread.start()
        self.active_downloads[task['id']] = thread
        
        window.evaluate_js(f"updateTaskStatus('{task['id']}', 'downloading')")
    
    def _download_video(self, task):
        try:
            video_info = task['video_info']
            ydl_opts = {
                'format': self._get_format_selector(task['format'], task['resolution']),
                'outtmpl': os.path.join(
                    self.download_folder,
                    f"%(title)s.%(ext)s"
                ),
                'progress_hooks': [self._progress_hook(task['id'])],
                'quiet': True,
                'no_warnings': True,
                'writethumbnail': task['download_thumbnail'],
                'writesubtitles': task['download_subtitles'],
                'allsubtitles': task['download_subtitles'],
                'subtitleslangs': ['all'] if task['download_subtitles'] else [],
                'postprocessors': [],
                'ffmpeg_location': self.ffmpeg_path
            }
            
            if task['download_thumbnail']:
                ydl_opts['postprocessors'].append({
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False
                })
            
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_info['webpage_url']])
                
            task['status'] = 'completed'
            task['progress'] = 100
            task['completed_at'] = datetime.now().isoformat()
            
            window.evaluate_js(f"updateTaskStatus('{task['id']}', 'completed')")
            window.evaluate_js(f"showNotification('{video_info['title']} - {self.get_translation('status.download_success')}', 'success')")
            
        except Exception as e:
            task['status'] = 'error'
            window.evaluate_js(f"updateTaskStatus('{task['id']}', 'error')")
            window.evaluate_js(f"showNotification('{self.get_translation('status.download_error')}: {str(e)}', 'error')")
            logging.error(f"Error downloading video {task['video_info']['title']}: {str(e)}")
            
        finally:
            self.active_downloads.pop(task['id'], None)
            self.start_download()
    
    def _get_format_selector(self, format_type, resolution):
        if format_type == "mp3":
            return "bestaudio/best"
        elif resolution:
            return f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]"
        else:
            return "bestvideo+bestaudio/best"
    
    def _progress_hook(self, task_id):
        def hook(d):
            if d['status'] == 'downloading':
                progress = d.get('_percent_str', '0%').strip('%')
                speed = d.get('_speed_str', '0 KB/s')
                eta = d.get('_eta_str', '--:--')
                
                try:
                    progress_float = float(progress)
                    window.evaluate_js(f"updateTaskProgress('{task_id}', {progress_float}, '{speed}', '{eta}')")
                    
                    task = next((t for t in self.download_queue if t['id'] == task_id), None)
                    if task:
                        task['progress'] = progress_float
                        task['speed'] = speed
                        task['eta'] = eta
                except ValueError:
                    pass
        return hook
    
    def pause_download(self, task_id):
        if task_id in self.active_downloads:
            thread = self.active_downloads[task_id]
            del self.active_downloads[task_id]
            
            task = next((t for t in self.download_queue if t['id'] == task_id), None)
            if task:
                task['status'] = 'paused'
                window.evaluate_js(f"updateTaskStatus('{task_id}', 'paused')")
    
    def cancel_download(self, task_id):
        if task_id in self.active_downloads:
            thread = self.active_downloads[task_id]
            del self.active_downloads[task_id]
            
        task = next((t for t in self.download_queue if t['id'] == task_id), None)
        if task:
            self.download_queue.remove(task)
            window.evaluate_js(f"removeTaskFromList('{task_id}')")
    
    def clear_queue(self):
        for task in self.download_queue[:]:
            if task['status'] == 'queued':
                self.download_queue.remove(task)
        
        window.evaluate_js("updateQueue([])")
    
    def cancel_all_downloads(self):
        for task_id in list(self.active_downloads.keys()):
            self.cancel_download(task_id)
    
    def get_queue(self):
        return [
            [
                task['id'],
                task['video_info']['title'],
                task['video_info']['extractor'],
                task['format'],
                task['resolution'],
                task['video_info']['thumbnail'],
                task['status'],
                task['progress'],
                task['speed'],
                task['eta']
            ]
            for task in self.download_queue
        ]
    
    def set_download_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.download_folder = folder_path
            self.save_settings()
            return True
        return False
    
    def set_language(self, language):
        if language in ['en', 'ru']:
            self.language = language
            self.save_settings()
            return True
        return False

def create_window():
    global window
    window = webview.create_window(
        'ClipTide',
        url='data/ui/new/index.html',
        js_api=downloader,
        width=1200,
        height=800,
        min_size=(800, 600),
        text_select=True
    )

if __name__ == '__main__':
    downloader = VideoDownloader()
    create_window()
    webview.start(debug=True)