import os
import sys
import shutil
import requests
import zipfile
import json
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QProgressBar
from PyQt6.QtGui import QIcon

# Настройки
GITHUB_REPO = "Rayness/YT-Downloader"  # Укажи свой репозиторий
GITHUB_TOKEN = None  # Если нужно, укажи GitHub Token
VERSION_FILE = "./data/version.txt"
DOWNLOAD_DIR = "update_tmp"  # Временная папка для архива
EXTRACT_DIR = "update_extract"  # Папка для распаковки
APP_EXECUTABLE = "YT-Downloader.exe"  # Заменить на свою программу

HEADERS = {
    "User-Agent": "Updater-App",
    "Accept": "application/vnd.github.v3+json"
}

class UpdaterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Updater")
        self.setGeometry(500, 300, 400, 350)
        layout = QVBoxLayout()
        self.setWindowIcon(QIcon("icon.ico"))

        self.label_status = QLabel("\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0439...")
        layout.addWidget(self.label_status)

        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.btn_check = QPushButton("\ud83d\udd0d \u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c")
        self.btn_check.clicked.connect(self.check_for_update)
        layout.addWidget(self.btn_check)

        self.btn_update = QPushButton("\u2b07\ufe0f \u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c")
        self.btn_update.setEnabled(False)
        self.btn_update.clicked.connect(self.update_program)
        layout.addWidget(self.btn_update)

        self.btn_launch = QPushButton("\ud83d\udd04 \u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c")
        self.btn_launch.clicked.connect(self.launch_program)
        layout.addWidget(self.btn_launch)

        self.setLayout(layout)
        self.check_for_update()

    def log(self, message):
        self.log_box.append(message)
        print(message)

    def get_local_version(self):
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as file:
                return file.read().strip()
        return "0.0.0"

    def update_local_version(self, new_version):
        with open(VERSION_FILE, "w") as file:
            file.write(new_version)

    def get_latest_version(self):
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("tag_name", "0.0.0")
        self.log(f"\u041e\u0448\u0438\u0431\u043a\u0430 GitHub API: {response.status_code}")
        print(response)
        return "0.0.0"

    def get_latest_release(self):
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, headers=HEADERS)

        if response.status_code == 200:
            release_data = response.json()
            assets = release_data.get("assets", [])
            if assets:
                return assets[0]["browser_download_url"]
        return None

    def check_for_update(self):
        local = self.get_local_version()
        latest = self.get_latest_version()

        if local != latest:
            url = self.get_latest_release()
            if url:
                self.label_status.setText("\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435!")
                self.btn_update.setEnabled(True)
            else:
                self.label_status.setText("\u0423 \u0432\u0430\u0441 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u044f\u044f \u0432\u0435\u0440\u0441\u0438\u044f.")
        else:
            self.label_status.setText("У вас последняя версия")

    def download_file(self, url, filename):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        if response.status_code == 200:
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    downloaded += len(chunk)
                    progress = int((downloaded / total_size) * 100)
                    self.progress.setValue(progress)
            return True
        return False

    def launch_program(self):
        if os.path.exists(APP_EXECUTABLE):
            subprocess.Popen([APP_EXECUTABLE], creationflags=subprocess.DETACHED_PROCESS)
        else:
            self.log("\u041d\u0435\u0442 \u0444\u0430\u0439\u043b\u0430 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b!")

    def update_program(self):
        latest = self.get_latest_version()
        url = self.get_latest_release()
        if not url:
            return

        archive_path = os.path.join(DOWNLOAD_DIR, "update.zip")
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        if self.download_file(url, archive_path):
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)

            for item in os.listdir(EXTRACT_DIR):
                src_path = os.path.join(EXTRACT_DIR, item)
                dst_path = os.path.join(os.getcwd(), item)
                
                if os.path.isdir(src_path):
                    if os.path.exists(dst_path):
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

            shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
            shutil.rmtree(EXTRACT_DIR, ignore_errors=True)

            self.label_status.setText("\u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u043e!")
            self.launch_program()
            self.update_local_version(latest)
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UpdaterGUI()
    window.show()
    print(window.get_latest_version())
    print(window.get_local_version())
    sys.exit(app.exec())
