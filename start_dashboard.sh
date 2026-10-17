#!/bin/bash
cd "$(dirname "$0")"
echo "🎬 YouTube Shorts Otomasyon Kontrol Paneli Başlatılıyor..."
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8502
