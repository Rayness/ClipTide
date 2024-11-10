@echo off
setlocal enabledelayedexpansion

rem Получаем язык системы
for /f "tokens=2 delims==" %%I in ('"wmic os get locale /value"') do set locale=%%I

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