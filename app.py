import os
import subprocess
import sys
from pathlib import Path

#Функция для указания пути к файлу
def downloadPath():
    os.environ

#Функция для создания папки
def create_folder(folder_name):
    try:
        os.makedirs(folder_name, exist_ok=True)
        print("Папка создана")
    except Exception as e:
        print("Ошибка при создании папки: {e}")

# Функция для открытия папки
def open_folder(folder_path):
    try:
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder_path])
        else:
            subprocess.run(["xdg-open", folder_path])
        print(f"Открыта папка: {folder_path}")
    except Exception as e:
        print(f"Ошибка при открытии папки: {e}")

# Функция для создания пустого файла
def create_file(file_name):
    try:
        with open(file_name, "w") as f:
            pass
        print(f"Файл '{file_name}' создан.")
    except Exception as e:
        print(f"Ошибка при создании файла: {e}")

# Функция для записи данных в файл
def write_to_file(file_name, content):
    try:
        with open(file_name, "w") as f:
            f.write(content)
        print(f"Данные записаны в файл '{file_name}'.")
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")