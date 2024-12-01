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
)

python app.py

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

:py-install
    echo Скачивание установщика...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.6/python-3.10.6.exe' -OutFile 'python-installer.exe'"
    
    echo Запуск установщика...
    python-installer.exe /passive InstallAllUsers=1 PrependPath=1
    
    echo Удаление установщика...
    del python-installer.exe

    echo Python установлен!
    goto checking

:End
    echo Выход из программы...
    timeout /t 1 /nobreak >nul
    exit