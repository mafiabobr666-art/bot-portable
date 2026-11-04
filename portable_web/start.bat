@echo off
title ЛОКАЛЬНЫЕ ЛОГИ ОРБИКС
color 0A
echo Проверка обновлений...

:: Ссылка на твой ZIP-архив с GitHub
set GITHUB_ZIP_URL=https://github.com/mafiabobr666-art/bot-portable/archive/refs/heads/main.zip

:: Скачиваем архив
powershell -Command "Invoke-WebRequest -Uri '%GITHUB_ZIP_URL%' -OutFile 'update.zip'"

:: Если архив скачался, распаковываем
if exist update.zip (
    echo Распаковка обновлений...
    powershell -Command "Expand-Archive -Path 'update.zip' -DestinationPath 'temp_update' -Force"
    
    :: Копируем файлы из вложенной папки (bot-portable-main/portable_web/*) в текущую папку
    if exist "temp_update\bot-portable-main\portable_web" (
        xcopy /Y /E /Q "temp_update\bot-portable-main\portable_web\*" .
    ) else (
        xcopy /Y /E /Q "temp_update\*" .
    )
    
    :: Удаляем временные файлы
    rmdir /S /Q temp_update
    del update.zip
    echo Обновления установлены!
)

echo Запуск сайта...
cd /d "%~dp0"
python -m pip install -r requirements.txt > nul 2>&1
start http://127.0.0.1:58339/?%1
python app.py
pause
