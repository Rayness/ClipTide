# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

import os
import sys
import shutil
import requests
import zipfile
import time
import subprocess
import psutil
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QProgressBar
from PyQt6.QtGui import QIcon

# Настройки
GITHUB_REPO = "Rayness/YT-Downloader"
VERSION_FILE = "./data/version.txt"
DOWNLOAD_DIR = "update_tmp"
EXTRACT_DIR = "update_extract"
APP_EXECUTABLE = "ClipTide.exe"
MAX_WAIT_TIME = 10  # Максимальное время ожидания завершения процесса (сек)

HEADERS = {"User-Agent": "Updater-App", "Accept": "application/vnd.github.v3+json"}

class UpdaterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.check_for_update()

    def setup_ui(self):
        self.setWindowTitle("Updater")
        self.setGeometry(500, 300, 400, 350)
        layout = QVBoxLayout()
        self.setWindowIcon(QIcon("icon.ico"))

        self.label_status = QLabel("Проверка обновлений...")
        layout.addWidget(self.label_status)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.btn_check = QPushButton("🔍 Проверить")
        self.btn_check.clicked.connect(self.check_for_update)
        layout.addWidget(self.btn_check)

        self.btn_update = QPushButton("⏬ Обновить")
        self.btn_update.setEnabled(False)
        self.btn_update.clicked.connect(self.update_program)
        layout.addWidget(self.btn_update)

        self.btn_launch = QPushButton("🔄 Запустить")
        self.btn_launch.clicked.connect(self.launch_program)
        layout.addWidget(self.btn_launch)

        self.setLayout(layout)

    def log(self, message):
        self.log_box.append(message)
        QApplication.processEvents()  # Обновляем GUI
        print(message)

    def get_local_version(self):
        try:
            if os.path.exists(VERSION_FILE):
                with open(VERSION_FILE, "r") as file:
                    return file.read().strip()
        except Exception as e:
            self.log(f"Ошибка чтения версии: {e}")
        return "0.0.0"

    def update_local_version(self, new_version):
        try:
            os.makedirs(os.path.dirname(VERSION_FILE), exist_ok=True)
            with open(VERSION_FILE, "w") as file:
                file.write(new_version)
        except Exception as e:
            self.log(f"Ошибка сохранения версии: {e}")

    def get_latest_version(self):
        try:
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(api_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.json().get("tag_name", "0.0.0")
            self.log(f"Ошибка GitHub API: {response.status_code}")
        except Exception as e:
            self.log(f"Ошибка проверки обновлений: {e}")
        return "0.0.0"

    def get_latest_release(self):
        try:
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(api_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                assets = response.json().get("assets", [])
                if assets:
                    return assets[0]["browser_download_url"]
        except Exception as e:
            self.log(f"Ошибка получения ссылки: {e}")
        return None

    def check_for_update(self):
        self.btn_update.setEnabled(False)
        local = self.get_local_version()
        latest = self.get_latest_version()

        if local != latest:
            url = self.get_latest_release()
            if url:
                self.label_status.setText(f"Доступно обновление {latest}!")
                self.btn_update.setEnabled(True)
                self.log(f"Текущая версия: {local}, Новая версия: {latest}")
            else:
                self.label_status.setText("Не удалось получить обновление")
        else:
            self.label_status.setText("У вас последняя версия")

    def download_file(self, url, filename):
        try:
            response = requests.get(url, stream=True, timeout=30)
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks

            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        progress = int((downloaded / total_size) * 100)
                        self.progress.setValue(progress)
                        QApplication.processEvents()
            return True
        except Exception as e:
            self.log(f"Ошибка загрузки: {e}")
            return False

    def terminate_process(self, process_name):
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == process_name:
                    proc.terminate()
                    proc.wait(timeout=5)
        except Exception as e:
            self.log(f"Ошибка завершения процесса: {e}")

    def launch_program(self):
        self.terminate_process(APP_EXECUTABLE)
        try:
            if os.path.exists(APP_EXECUTABLE):
                subprocess.Popen([APP_EXECUTABLE], shell=True)
                self.log("Программа запущена")
                self.close()
            else:
                self.log("Файл программы не найден!")
        except Exception as e:
            self.log(f"Ошибка запуска: {e}")

    def safe_copy(self, src, dst):
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
            return True
        except Exception as e:
            self.log(f"Ошибка копирования {src}: {e}")
            return False

    def update_program(self):
        self.btn_update.setEnabled(False)
        latest = self.get_latest_version()
        url = self.get_latest_release()
        
        if not url:
            self.log("Не удалось получить ссылку на обновление")
            return

        # Создаем временные директории
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(EXTRACT_DIR, exist_ok=True)
        
        archive_path = os.path.join(DOWNLOAD_DIR, "update.zip")
        self.log(f"Загрузка обновления {latest}...")
        
        if not self.download_file(url, archive_path):
            return

        self.log("Распаковка архива...")
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Извлекаем в EXTRACT_DIR, сохраняя структуру
                zip_ref.extractall(EXTRACT_DIR)
        except Exception as e:
            self.log(f"Ошибка распаковки: {e}")
            return

        # Закрываем основное приложение
        self.terminate_process(APP_EXECUTABLE)
        time.sleep(1)  # Даем время на завершение

        self.log("Применение обновления...")
        try:
            # Копируем все файлы из EXTRACT_DIR в текущую директорию
            for root, dirs, files in os.walk(EXTRACT_DIR):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, EXTRACT_DIR)
                    dst_path = os.path.join(os.getcwd(), rel_path)
                    
                    # Пропускаем файлы, которые не должны обновляться
                    if os.path.basename(dst_path) in ['config.ini', 'settings.json']:
                        continue
                        
                    self.safe_copy(src_path, dst_path)
            
            self.log("Очистка временных файлов...")
            shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
            shutil.rmtree(EXTRACT_DIR, ignore_errors=True)
            
            self.update_local_version(latest)
            self.label_status.setText("Обновление завершено!")
            self.btn_launch.setEnabled(True)
            self.log(f"Успешно обновлено до версии {latest}")
            
        except Exception as e:
            self.log(f"Критическая ошибка обновления: {e}")
            self.label_status.setText("Ошибка обновления!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UpdaterGUI()
    window.show()
    sys.exit(app.exec())