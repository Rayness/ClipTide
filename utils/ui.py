import webview
from utils.utils import get_local_version

version = get_local_version()

def createwindow(html_file_path, api):
    # Создаем окно с HTML-контентом
    window = webview.create_window(
        f'ClipTide {version}',
        html_file_path,
        js_api=api, # Передаем API для взаимодействия с JavaScript
        height=780,
        width=1000,
        resizable=True,
        text_select=True
    )

    return window