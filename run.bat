@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion 
rem Получаем язык системы
for /f "tokens=2 delims==" %%I in ('"wmic os get locale /value"') do set locale=%%I

:checking
rem Проверяем, установлен ли Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    goto py-install-menu
) else (
    echo Python уже установлен.
    python checks.py
    if not exist downloads (
        mkdir downloads
        set download_folder="downloads"
        echo Папка "downloads" создана и выбрана по умолчанию. 
        echo %download_folder% > path.txt
    ) else (
        echo Папка "downloads" уже существует.
        set /p download_folder=<path.txt
    )
    echo Переход к меню
    goto menu
)

:py-install-menu
    echo Python не найден.
    echo.
    echo Выберите дальнейшее действие:
    echo.
    echo -----------------------------------------------------------------------------------------
    echo [1] - Установить Python в ручную | Рекомендуется скачать актуальную версию не нижу 3.10.6
    echo [2] - Установить Python в автоматическом формате | Будет установлена версия 3.10.6
    echo -----------------------------------------------------------------------------------------
    echo [0]   Отменить установку и закрыть приложение
    echo.
    set /p cho="Введите ваш выбор и нажмите 'Enter'"
    if %cho%==1 goto manual-install
    if %cho%==2 goto py-install
    if %cho%==0 goto End

:menu
    echo Меню загружено
    echo.
    echo Текущие варианты:
    echo.
    echo -----------------------------------------------------------------------
    echo [1] - Скачать аудио в формате .mp3 --- Максимальное качество звука 
    echo [2] - Скачать видео в формате .mp4 --- HD - 4K
    echo -----------------------------------------------------------------------
    echo [3] - Настройки
    echo -----------------------------------------------------------------------
    echo [0] - Выход
    echo.
    set /p choice="Введите ваш выбор и нажмите 'Enter': "

if %choice%==1 goto Download-mp3
if %choice%==2 goto Download-mp4
if %choice%==3 goto settings
if %choice%==0 goto End

:manual-install
    echo Для ручной установки Python перейдите по ссылке: https://www.python.org/downloads/ и выберите 'Download Python *.**.*', где * - текущая версия. || Например: 3.10.6, у вас будет более старшая версия
    echo.
    echo Во время установки обязательно установите галочку Add to PATH. Без этого программа не будет работать, как и другие Python приложения.
    echo.
    echo Если после ручной установки в процессе выполнения программы возникают какие-то ошибки, рекомендуется удалить текущую версию Python и выполнить установку в автоматическом режиме.
    echo.
    echo Выполните установку Python после чего нажмите любую кнопку для возвращения в прогромму...
    pause >nul
    goto checking

:settings
    echo.
    echo Настройки
    echo.
    echo Выбор папки для сохранения скаченных файлов:
    echo.
    echo Текущая папка для загрузки файлов: "%download_folder%"
    echo --------------------------------------------------------------------------------
    echo [1] - Папка по умолчанию (будет создана папка "downloads" в папке с программой)
    echo [2] - Указать свой вариант (например, "C:\\downloads'):")
    echo --------------------------------------------------------------------------------
    echo [0] - Выход 
    echo.
    set /p choi="Введите ваш выбор и нажмите 'Enter': "

    if %choi%==1 (
        set download_folder="downloads"
        echo.
        echo Путь был обновлен
        echo %download_folder% > path.txt
        pause
        goto menu
    )
    if %choi%==2 goto settings_manual
    if %choi%==0 goto menu

:settings_manual
    echo.
    echo Укажите папку для скачивания (например - "C:\\downloads'):"): 
    echo.
    set /p download_folder="Вставьте сюда путь к папке: "
    echo.
    echo Путь был обновлен
    echo %download_folder% > path.txt
    pause
    goto menu

:py-install
    echo Скачивание установщика...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.6/python-3.10.6.exe' -OutFile 'python-installer.exe'"
    
    echo Запуск установщика...
    python-installer.exe /passive InstallAllUsers=1 PrependPath=1
    
    echo Удаление установщика...
    del python-installer.exe

    echo Python установлен!
    goto checking

:Download-mp4
    echo.
    echo ВНИМАНИЕ: Если вы живете в России, то с загрузкой 100% возникнут сложности и проблемы.
    echo Для решения данной проблемы рекомендуется использовать сами знаете что (VPN), ибо с zapret всё работает так же нестабильно.
    echo.
    echo Выберите предпочтительное разрешение:
    echo ----------------------------------------------------
    echo [1] - 720p || HD
    echo [2] - 1080p || FHD
    echo [3] - 1440p || 2K - если поддерживается видео
    echo [4] - 2160p || 4K - если поддерживается видео
    echo ----------------------------------------------------
    echo.
    echo.
    echo 0 - Назад
    set /p res_choice="Введите разрешение: "
    
if %res_choice%==1 set resolution=720p
if %res_choice%==2 set resolution=1080p
if %res_choice%==3 set resolution=1440p
if %res_choice%==4 set resolution=2160p
if %res_choice%==0 goto menu

echo Выбрано разрешение: !resolution!
set /p URL="Введите ссылку на YouTube видео, которое хотите скачать в .mp4: "
echo Ваша ссылка: "%URL%"
python mp4.py "%URL%" !resolution! "%download_folder%"
goto Download-Complete

:Download-mp3
    set /p URL="Введите ссылку на YouTube видео, которое хотите скачать в .mp3: "
    python mp3.py "%URL%" "%download_folder%"
    goto Download-Complete

:End
    echo Выход из программы...
    timeout /t 1 /nobreak >nul
    exit

:Download-Complete
    start "" "%download_folder%"
    echo Загрузка завершена! Возвращение в меню через 4 секунды...
    timeout /t 4 /nobreak >nul
    goto menu


