@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion 
rem Получаем язык системы
for /f "tokens=2 delims==" %%I in ('"wmic os get locale /value"') do set locale=%%I

:cheking
rem Проверяем, установлен ли Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    goto py-install-menu
) else (
    echo Python уже установлен.
    python checks.py
    goto menu   
)


:py-install-menu
    echo Python не найден.
    echo.
    echo Выберите дальнейшее действие:
    echo.
    echo 1 - Установить Python в ручную | Рекомендуется скачать актуальную версию не нижу 3.10.6
    echo 2 - Установить Python в автоматическом формате | Будет установлена версия 3.10.6
    echo.
    set /p cho="Введите ваш выбор и нажмите 'Enter'"
    if %cho%==1 goto manual-install
    if %cho%==2 goto py-install

:menu
    echo.
    echo Текущие варианты:
    echo.
    echo 1 - скачивание аудиофайла в формате .mp3
    echo -----------------------------------------------------------------------
    echo 2 - скачивание видео в формате .mp4 - HD -- 720p || в разработке
    echo 3 - скачивание видео в формате .mp4 - FullHD -- 1080p || в разработке
    echo 4 - скачивание видео в формате .mp4 - 2K -- 1440p || в разработке
    echo 5 - скачивание видео в формате .mp4 - 4K -- 2160p || в разработке
    echo -----------------------------------------------------------------------
    echo 0 - Выход
    echo.

set /p choice="Введите ваш выбор и нажмите 'Enter': "

if %choice%==1 goto Download-mp3
if %choice%==0 goto End

goto Not-ready

:manual-install
    echo Для ручной установки Python перейдите по ссылке: https://www.python.org/downloads/ и выберите 'Download Python *.**.*', где * - текущая версия. || Например: 3.10.6, у вас будет более старшая версия
    echo.
    echo Во время установки обязательно установите галочку Add to PATH. Без этого программа не будет работать, как и другие Python приложения.
    echo.
    echo Если после ручной установки в процессе выполнения программы возникают какие-то ошибки, рекомендуется удалить текущую версию Python и выполнить установку в автоматическом режиме.
    echo.
    echo Выполните установку Python после чего нажмите любую кнопку для возвращения в прогромму...
    pause >nul
    goto cheking

:py-install
    echo Скачивание установщика...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.6/python-3.10.6.exe' -OutFile 'python-installer.exe'"
    
    echo Запуск установщика...
    python-installer.exe /passive InstallAllUsers=1 PrependPath=1
    
    echo Удаление установщика...
    del python-installer.exe

    echo Python установлен!
    goto checking


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
    echo Загрузка завершена! Нажмите любую клавишу для продолжения...
    pause >nul
    goto menu


