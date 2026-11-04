@echo off
title ЛОКАЛЬНЫЕ ЛОГИ ОРБИКС
color 0A
echo Проверка обновлений...

:: 🔴 ВСТАВЬ СЮДА ССЫЛКУ НА СКАЧИВАНИЕ ZIP С ТВОЕГО GITHUB 🔴
:: Пример: https://github.com/твой_ник/твой_репо/archive/refs/heads/main.zip
set GITHUB_ZIP_URL=https://github.com/mafiabobr666-art/bot-portable/archive/refs/heads/main.zip

:: Скачиваем архив через PowerShell (встроен в Windows)
powershell -Command "Invoke-WebRequest -Uri '%GITHUB_ZIP_URL%' -OutFile 'update.zip'"
if exist update.zip (
    echo Распаковка обновлений...
    powershell -Command "Expand-Archive -Path 'update.zip' -DestinationPath 'temp_update' -Force"
    xcopy /Y /E /Q "temp_update\*" .
    rmdir /S /Q temp_update
    del update.zip
)

echo Запуск сайта...
cd /d "%~dp0"
python -m pip install -r requirements.txt > nul 2>&1
start http://127.0.0.1:58339/?%1
python app.py
pause
