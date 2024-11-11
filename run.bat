@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion 
rem Получаем язык системы
for /f "tokens=2 delims==" %%I in ('"wmic os get locale /value"') do set locale=%%I

rem Проверяем, установлен ли Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Python не найден. Начинаю установку...

    rem Скачиваем установщик
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.6/python-3.10.6.exe' -OutFile 'python-installer.exe'"
    
    rem Запускаем установку
    python-installer.exe /passive InstallAllUsers=1 PrependPath=1
    
    rem Удаляем установочный файл
    del python-installer.exe

    echo Python установлен!
) else (
    echo Python уже установлен.
)

:menu
    echo Текущие варианты:
    echo 1 - скачивание аудиофайла в формате .mp3
    echo -----------------------------------------------------------------------
    echo 2 - скачивание видео в формате .mp4 - HD -- 720p (в разработке)
    echo 3 - скачивание видео в формате .mp4 - FullHD -- 1080p (в разработке)
    echo 4 - скачивание видео в формате .mp4 - 2K -- 1440p (в разработке)
    echo 5 - скачивание видео в формате .mp4 - 4K -- 2160p (в разработке)
    echo -----------------------------------------------------------------------
    echo 0 - Выход
    echo.

set /p choice="Введите ваш выбор и нажмите 'Enter': "

if %choice%==1 goto Download-mp3
if %choice%==0 goto End

goto Not-ready

:Download-mp3
    set /p URL="Введите ссылку на YouTube видео, которое хотите скачать в .mp3: "
    python app.py %URL%
    goto Download-Complete

:Not-ready
    echo Выбранный вами вариант ещё в разработке, либо не существует
    echo Нажмите любую клавишу, чтобы вернуться в меню...
    pause >nul
    goto menu

:End
    echo Выход из программы...
    timeout /t 1 /nobreak >nul
    exit

:Download-Complete
    if "%locale%"=="1049" (
        echo Загрузка завершена! Нажмите любую клавишу для продолжения...
    ) else (
        echo Download complete, press any button to continue...
    )
    pause >nul


