import subprocess
import urllib.parse
from typing import Optional


class SafariBridge:
    def open_in_safari(self, url: str = "https://labs.google/fx/tools/video-fx"):
        """Safari'de (kullanıcının zaten giriş yaptığı tarayıcıda) Google Labs'i açar."""
        cmd = ["osascript", "-e", f'tell application "Safari" to open location "{url}"']
        try:
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            print(f"[SafariBridge] Safari açma hatası: {e}")
            import webbrowser
            webbrowser.open(url)
            return True

    def copy_to_clipboard_and_notify(self, text: str, notification_title: str = "3D Prompt Kopyalandı!"):
        """Prompt'u doğrudan macOS panosuna kopyalar ve bildirim gösterir."""
        # pbcopy ile panoya kopyala
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(text.encode("utf-8"))

        # macOS Bildirimi
        safe_title = notification_title.replace('"', '\\"')
        safe_msg = "Prompt panoya kopyalandı, Safari'de Google Labs'e yapıştırıp indirebilirsiniz.".replace('"', '\\"')
        cmd = ["osascript", "-e", f'display notification "{safe_msg}" with title "{safe_title}"']
        try:
            subprocess.run(cmd, check=True)
        except Exception:
            pass
