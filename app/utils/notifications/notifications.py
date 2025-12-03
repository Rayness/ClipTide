# app/utils/notifications/notifications.py

from datetime import datetime
import json
import os
import winsound
from app.utils.const import NOTIFICATION_FILE

def load_notifications():
    path = NOTIFICATION_FILE
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_notifications(notifications):
    try:
        with open(NOTIFICATION_FILE, "w", encoding="utf-8") as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving notifications: {e}")

# Добавили аргумент payload=None
def add_notification(title, message, source, type="local", payload=None):
    notifications = load_notifications()
    
    new_notification = {
        "id": f"{int(datetime.now().timestamp() * 1000)}", # Уникальный ID на основе времени
        "type": type,
        "title": title,
        "message": message,
        "source": source,
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M"), # Читаемая дата сразу
        "read": "False",
        "payload": payload or {} # Данные видео (url, thumb, etc)
    }
    
    # Ограничим историю, например, последними 50 записями, чтобы файл не пух
    if len(notifications) > 50:
        notifications.pop(0)

    notifications.append(new_notification)
    save_notifications(notifications)
    
    try:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except:
        pass
        
    return notifications

def delete_notification(notification_id):
    data = load_notifications()
    data = [notif for notif in data if notif["id"] != notification_id]
    save_notifications(data)
    return data

def mark_notification_as_read(notification_id):
    data = load_notifications()
    for notif in data:
        if notif["id"] == notification_id:
            notif["read"] = "True"
            break
    save_notifications(data)
    return data