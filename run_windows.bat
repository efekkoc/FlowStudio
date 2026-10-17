@echo off
title YouTube Shorts AI Studio Pro
echo ============================================================
echo 🎬 YouTube Shorts AI Studio Pro - Windows Baslatici
echo ============================================================

if not exist ".venv" (
    echo [1/2] Sanal ortam olusturuluyor...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [2/2] Paketler yukleniyor...
    pip install -r requirements.txt
    pip install pywebview
) else (
    call .venv\Scripts\activate.bat
)

echo [OK] Uygulama baslatiliyor...
python desktop_app.py
pause
