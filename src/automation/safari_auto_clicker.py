import time
import subprocess
from pathlib import Path


class SafariAutoClicker:
    def __init__(self):
        pass

    def send_prompt_to_safari(self, prompt: str):
        """
        macOS AppleScript ve Safari aracılığıyla:
        1. Promptu panoya alır.
        2. Safari'yi öne getirir ve Google Labs'e gider.
        3. 2.5 saniye sonra otomatik yapıştırıp (Cmd+V) Enter'a basar.
        """
        # Panoya kopyala
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(prompt.encode("utf-8"))

        applescript = """
        tell application "Safari"
            activate
            open location "https://labs.google/fx/tools/video-fx"
        end tell
        delay 2.5
        tell application "System Events"
            tell process "Safari"
                keystroke "v" using {command down}
                delay 0.5
                key code 36
            end tell
        end tell
        """

        try:
            subprocess.run(["osascript", "-e", applescript], check=True)
            return True
        except Exception as e:
            print(f"[SafariAutoClicker] AppleScript hatası: {e}")
            # Basit fallback: Sadece Safari'yi aç
            subprocess.run(["osascript", "-e", 'tell application "Safari" to open location "https://labs.google/fx/tools/video-fx"'])
            return False
