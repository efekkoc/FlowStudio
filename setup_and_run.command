#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "============================================================"
echo "🎬 YouTube Shorts AI Studio Pro - Otomatik Kurulum ve Başlatma"
echo "============================================================"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "❌ HATA: Bilgisayarınızda Python 3 bulunamadı. Lütfen python.org adresinden Python yükleyin."
    read -p "Çıkmak için Enter'a basın..."
    exit 1
fi

# Sanal ortam kontrolü ve kurulumu
if [ ! -d ".venv" ]; then
    echo "📦 İlk kurulum yapılıyor, sanal ortam oluşturuluyor..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "📦 Bağımlılıklar yükleniyor (Bu işlem ilk seferde 1-2 dakika sürebilir)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pywebview
else
    source .venv/bin/activate
fi

# Uygulamayı Başlat
echo "🚀 Masaüstü Uygulaması Başlatılıyor..."
python desktop_app.py
