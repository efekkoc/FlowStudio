#!/usr/bin/env python3
"""
Flow Studio — Native macOS Desktop App Launcher
Powered by PyWebView & Apple WebKit
"""

import os
import sys
import time
import signal
import atexit
import subprocess
import urllib.request
from pathlib import Path

# Workspace dizinini çalışma dizini yap
APP_DIR = Path(__file__).resolve().parent
os.chdir(APP_DIR)

STREAMLIT_PORT = 8502
HEALTH_URL = f"http://127.0.0.1:{STREAMLIT_PORT}/_stcore/health"
APP_URL = f"http://127.0.0.1:{STREAMLIT_PORT}"

streamlit_process = None


def is_server_running() -> bool:
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "FlowStudioLauncher"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_streamlit_server():
    global streamlit_process
    if is_server_running():
        print("[FlowStudio] Streamlit servisi zaten 8502 portunda aktif.")
        return

    print("[FlowStudio] Streamlit servisi başlatılıyor...")
    venv_streamlit = APP_DIR / ".venv" / "bin" / "streamlit"
    cmd = [
        str(venv_streamlit if venv_streamlit.exists() else "streamlit"),
        "run",
        str(APP_DIR / "dashboard" / "app.py"),
        "--server.port", str(STREAMLIT_PORT),
        "--server.headless", "true",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ]

    env = os.environ.copy()
    env["HOME"] = str(APP_DIR)
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    streamlit_process = subprocess.Popen(
        cmd,
        cwd=str(APP_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Sağlık kontrolü için bekle (Maks 15 saniye)
    for _ in range(30):
        if is_server_running():
            print("[FlowStudio] Streamlit servisi hazır!")
            return
        time.sleep(0.5)

    print("[FlowStudio] Uyarı: Sunucu sağlık kontrolü zaman aşımına uğradı, yine de pencere açılıyor...")


def cleanup():
    global streamlit_process
    if streamlit_process:
        print("[FlowStudio] Streamlit servisi kapatılıyor...")
        try:
            streamlit_process.terminate()
            streamlit_process.wait(timeout=3)
        except Exception:
            streamlit_process.kill()


atexit.register(cleanup)


def main():
    start_streamlit_server()

    try:
        import webview
    except ImportError:
        print("[FlowStudio] pywebview modülü bulunamadı, tarayıcıda açılıyor...")
        import webbrowser
        webbrowser.open(APP_URL)
        return

    print("[FlowStudio] macOS WebKit yerel penceresi açılıyor...")
    window = webview.create_window(
        title="Flow Studio — AI 3D Shorts Studio",
        url=APP_URL,
        width=1400,
        height=920,
        min_size=(1100, 720),
        background_color="#06080D",
        text_select=True,
        zoomable=True
    )

    # WebKit yerel penceresini başlat
    webview.start(debug=False)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    main()
