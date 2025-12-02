# app/utils/queue/queue.py

import os
import json
import uuid

from app.utils.const import QUEUE_FILE

def load_queue_from_file():
    """ Загружаем очередь из JSON-файла с миграцией старых данных. """
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8", errors="ignore") as file:
            try:
                data = json.load(file)
                
                # --- БЛОК МИГРАЦИИ ---
                clean_data = []
                for item in data:
                    # Если элемент уже словарь (новый формат) - оставляем
                    if isinstance(item, dict):
                        clean_data.append(item)
                    
                    # Если элемент список (старый формат), конвертируем
                    elif isinstance(item, list) and len(item) >= 5:
                        # Старый формат: [url, title, fmt, res, thumb]
                        print("Migrating old queue item...")
                        clean_data.append({
                            "id": str(uuid.uuid4()),
                            "url": item[0],
                            "title": item[1],
                            "format": item[2],
                            "resolution": item[3],
                            "thumbnail": item[4],
                            "status": "queued", # Ставим статус "в очереди"
                            "fmt_label": "Format", # Дефолтные значения
                            "res_label": "Resolution"
                        })
                
                return clean_data
                # ---------------------

            except json.JSONDecodeError:
                return []
            except Exception as e:
                print(f"Error loading queue: {e}")
                return []
    return []

def save_queue_to_file(queue):
    """
    Сохраняет очередь загрузки в JSON-файл.
    """
    try:
        with open(QUEUE_FILE, "w", encoding="utf-8", errors="ignore") as file:
            json.dump(queue, file, ensure_ascii=False, indent=4)
            # print("Очередь загрузки сохранена.")
    except Exception as e:
        print(f"Ошибка при сохранении очереди: {e}")