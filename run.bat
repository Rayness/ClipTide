@echo off
chcp 65001
setlocal enabledelayedexpansion
rem Получаем язык системы
for /f "tokens=2 delims==" %%I in ('"wmic os get locale /value"') do set locale=%%I

rem Проверяем, установлен ли Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python не найден. Начинаю установку...

    rem Скачиваем установщик Python
    set "URL=https://www.python.org/ftp/python/3.10.6/python-3.10.6.exe"
    set "INSTALLER=python-installer.exe"
    
    rem Скачиваем установщик
    powershell -Command "Invoke-WebRequest -Uri %URL% -OutFile %INSTALLER%"
    
    rem Запускаем установку
    start /wait %INSTALLER% /quiet InstallAllUsers=1 PrependPath=1
    
    rem Удаляем установочный файл
    del %INSTALLER%

    echo Python установлен!
) else (
    echo Python уже установлен.
)

rem Проверяем язык (например, "1049" — это русский)
if "%locale%"=="1049" (
    @echo off
    set /p URL="Вставьте ссылку на видео с YouTube: "
) else (
    @echo off
    set /p URL="Enter YouTube link here: "
)
python app.py %URL%
if "%locale%"=="1049" (
    echo Загрузка завершена! Нажмите любую клавишу для продолжения...
) else (
    echo Download complete, press any button to continue...
)
pause >nul