import os
import sys
import time
import subprocess
import threading
import urllib.request
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PORT = 8502
APP_URL = f"http://localhost:{PORT}"


def is_server_running():
    try:
        urllib.request.urlopen(APP_URL, timeout=1)
        return True
    except Exception:
        return False


def start_streamlit_server():
    if not is_server_running():
        python_exe = sys.executable
        cmd = [
            python_exe, "-m", "streamlit", "run",
            str(BASE_DIR / "dashboard" / "app.py"),
            "--server.port", str(PORT),
            "--server.headless", "true"
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc
    return None


def main():
    print("=" * 60)
    print("🎬 YouTube Shorts AI Studio Pro - Masaüstü Başlatılıyor...")
    print(f"🔗 Yerel Adres: {APP_URL}")
    print("=" * 60)

    server_proc = start_streamlit_server()

    # Sunucunun hazır olmasını bekle
    for _ in range(30):
        if is_server_running():
            break
        time.sleep(0.5)

    try:
        import webview
        print("🖥️ Bağımsız masaüstü penceresi açılıyor...")
        window = webview.create_window(
            title="YouTube Shorts AI Studio Pro",
            url=APP_URL,
            width=1320,
            height=900,
            resizable=True,
            min_size=(900, 600)
        )
        webview.start()
    except Exception as e:
        print(f"⚠️ Yerel pencere motoru ({e}), sistem tarayıcısında açılıyor...")
        webbrowser.open(APP_URL)

    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()
