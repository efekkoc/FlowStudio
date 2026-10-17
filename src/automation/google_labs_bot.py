import os
import time
from pathlib import Path
from typing import Optional
from config.settings import BASE_DIR

PROFILE_DIR = BASE_DIR / "google_labs_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


class GoogleLabsBot:
    def __init__(self, headless: bool = False):
        self.profile_dir = PROFILE_DIR
        self.headless = headless

    def _get_browser_args(self):
        return [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--start-maximized"
        ]

    def open_login_window(self):
        """
        Google'ın bot korumasını (güvenli olmayan tarayıcı uyarısı) aşan
        gerçek Chrome ve Stealth modunda giriş penceresi açar.
        """
        from playwright.sync_api import sync_playwright
        from playwright_stealth import stealth_sync

        with sync_playwright() as p:
            # Gerçek yüklü Google Chrome üzerinden başlat
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                channel="chrome",
                headless=False,
                ignore_default_args=["--enable-automation"],
                args=self._get_browser_args(),
                viewport=None
            )
            page = context.pages[0] if context.pages else context.new_page()
            stealth_sync(page)
            
            # Ekstra güvenlik bypass betiği
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.navigator.chrome = { runtime: {} };
            """)

            print("[GoogleLabsBot] Gerçek Chrome ile Google Labs VideoFX açılıyor...")
            page.goto("https://labs.google/fx/tools/video-fx")
            print("[GoogleLabsBot] Lütfen Google hesabınızla giriş yapın. Giriş tamamlandığında pencereyi kapatabilirsiniz.")

            # Pencere kapatılana kadar bekle
            try:
                while len(context.pages) > 0 and not page.is_closed():
                    time.sleep(1)
            except Exception:
                pass

            try:
                context.close()
            except Exception:
                pass

    def generate_and_download_video(
        self,
        master_prompt: str,
        output_video_path: str,
        timeout_seconds: int = 180
    ) -> bool:
        """
        Google Labs VideoFX'e otonom girerek promptu yapıştırır ve videoyu indirir.
        """
        from playwright.sync_api import sync_playwright
        from playwright_stealth import stealth_sync
        
        target_path = Path(output_video_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                channel="chrome",
                headless=self.headless,
                ignore_default_args=["--enable-automation"],
                args=self._get_browser_args(),
                viewport={"width": 1280, "height": 800}
            )
            page = context.pages[0] if context.pages else context.new_page()
            stealth_sync(page)

            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.navigator.chrome = { runtime: {} };
            """)

            try:
                print("[GoogleLabsBot] Google Labs VideoFX açılıyor...")
                page.goto("https://labs.google/fx/tools/video-fx", timeout=45000)
                page.wait_for_load_state("networkidle", timeout=30000)

                textarea = page.locator("textarea, input[type='text'], div[contenteditable='true']").first
                textarea.wait_for(state="visible", timeout=15000)
                textarea.fill(master_prompt)
                time.sleep(1)

                generate_btn = page.locator("button:has-text('Generate'), button:has-text('Create'), button[aria-label*='Generate']").first
                if generate_btn.is_visible():
                    generate_btn.click()
                else:
                    textarea.press("Enter")

                print("[GoogleLabsBot] Prompt gönderildi, video render bekleniyor...")

                video_elem = page.locator("video, a[download]").first
                video_elem.wait_for(state="attached", timeout=timeout_seconds * 1000)

                video_src = video_elem.get_attribute("src")
                if video_src:
                    import requests
                    r = requests.get(video_src, timeout=60)
                    with open(target_path, "wb") as f:
                        f.write(r.content)
                    context.close()
                    return True

            except Exception as e:
                print(f"[GoogleLabsBot] Hata/zaman aşımı: {e}")

            context.close()
            return False
