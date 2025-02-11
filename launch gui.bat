@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion 
rem Получаем язык системы
for /f "tokens=2 delims==" %%I in ('"wmic os get locale /value"') do set locale=%%I

python\python.exe gui.py