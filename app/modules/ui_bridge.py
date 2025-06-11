# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

class UIBridge:
    def __init__(self, window, translation):
        self.window = window
        self.translation = translation

    def set_status(self, key: str):
        status_text = self.translations.get('status', {}).get(key, "")
        self.window.evaluate_js(f'document.getElementById("status").innerText = {status_text}')

    def set_progress(self, progress):
        self.window.evaluate_js(f'document.getElementById("progress").innerText = "{self.translation['progress']} {progress}%"')
        self.window.evaluate_js(f'document.getElementById("progress-fill").style.width = "{progress}%"')

    def set_eta(self, seconds: int):
        eta_minutes = seconds // 60 if seconds is not None else 0
        eta_seconds = seconds % 60 if seconds is not None else 0
        eta_formatted = f"{self.translation.get('status', {}).get('download_ended')}" if seconds == 0 else f"{int(eta_minutes)} {self.translation['min']} {int(eta_seconds)} {self.translation['sec']}"

        self.window.evaluate_js(f'document.getElementById("eta").innerText = "{self.translations['eta']} {eta_formatted}"')
    
    def set_speed(self, speed: int):
        speed_mbps = speed / (1024 * 1024) if speed else 0
        speed_formatted = f"{speed_mbps:.2f} {self.translation['mbs']}"

        self.window.evaluate_js(f'document.getElementById("speed").innerText = "{self.translations['speed']} {speed_formatted}"')

    def reset_progress(self):
        self.set_progress(0)
        self.set_eta(0)
        self.set_speed(0)
        self.set_status("status_text")
        self.window.evaluate_js('hideSpinner()')

    def JS_Functions(self, func: str, key=""):
        self.window.evaluate_js(f'{func}("{key}")')

    def showSpinner(self):
        self.window.evaluate_js(f'showSpinner()')

    def hideSpinner(self):
        self.window.evaluate_js(f'hideSpinner()')