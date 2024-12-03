@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion 
rem Получаем язык системы
for /f "tokens=2 delims==" %%I in ('"wmic os get locale /value"') do set locale=%%I

rem Проверяем, установлен ли Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Скачивание установщика...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0.exe' -OutFile 'python-installer.exe'"
    
    echo Запуск установщика...
    python-installer.exe /passive InstallAllUsers=1 PrependPath=1
    
    echo Удаление установщика...
    del python-installer.exe

    echo Python установлен!
    goto checking
) else (
    echo Python уже установлен.
    python checks.py
)

python app.py