from datetime import datetime
import json
import os
import winsound

from app.utils.const import NOTIFICATION_FILE


def load_notifications():
        path = NOTIFICATION_FILE
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                print("Notifications: Файл был загружен")
                return json.load(f)
        return []

def save_notifications(notifications):
    with open(NOTIFICATION_FILE, "w", encoding="utf-8") as f:
        json.dump(notifications, f, ensure_ascii=False, indent=2)

def add_notification(title, message, source, type="local"):
    notifications = load_notifications()
    new_notification = {
        "id": f"{len(notifications) + 1}",
        "type": type,
        "title": title,
        "message": message,
        "source" : source,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "read": "False"
    }
    notifications.append(new_notification)
    save_notifications(notifications)
    winsound.MessageBeep(winsound.MB_ICONASTERISK) 
    return notifications

def delete_notification(notification_id):
    data = load_notifications()
    # Удаляем уведомление по id
    data = [notif for notif in data if notif["id"] != notification_id]
    # Сохраняем обратно
    save_notifications(data)


def mark_notification_as_read(notification_id):
    data = load_notifications()

    for notif in data:
        if notif["id"] == notification_id:
            notif["read"] = "True"
            break
    save_notifications(data)
    return data