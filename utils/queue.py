import os
import json

from utils.const import QUEUE_FILE

def load_queue_from_file():
    """ Загружаем очередь из JSON-файла. """
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8", errors="ignore") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                # window.evaluate_js(f'ERROR: {e}')
                return []
    return []

def save_queue_to_file(queue):
    """
    Сохраняет очередь загрузки в JSON-файл.
    """
    try:
        try:
            with open(QUEUE_FILE, "w", encoding="utf-8", errors="ignore") as file:
                json.dump(queue, file, ensure_ascii=False, indent=4)
                print("Очередь загрузки сохранена.")
        except UnicodeEncodeError as e:
            print(f"Ошибка кодировки: {e}. Проблемный символ: {e.object[e.start:e.end]}")
            # window.evaluate_js(f'ERROR: {e}')
    except Exception as e:
        print(f"Ошибка при сохранении очереди: {e}")
        # window.evaluate_js(f'ERROR: {e}')