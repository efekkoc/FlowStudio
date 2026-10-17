import os
import re
import time
import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

from config.settings import BASE_DIR, CANDIDATES_DIR
from src.generator.google_labs_prompter import GoogleLabsPrompter
from src.video_engine.video_enhancer import VideoEnhancer

CDP_PORT = 9222
CDP_URL = f"http://localhost:{CDP_PORT}"
CHROME_PROFILE = BASE_DIR / "chrome_flow_profile"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class FlowCDPBot:
    def __init__(self):
        self.prompter = GoogleLabsPrompter()
        self.enhancer = VideoEnhancer()
        self.profile_dir = CHROME_PROFILE
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    def is_chrome_running(self) -> bool:
        try:
            r = requests.get(f"{CDP_URL}/json/version", timeout=1)
            return r.status_code == 200
        except Exception:
            return False

    def start_chrome_daemon(self, target_url: str = "https://flow.google.com/"):
        """Chrome'u tek tıkta doğrudan Google Flow ile başlatır."""
        if not self.is_chrome_running():
            cmd = [
                CHROME_BIN,
                f"--remote-debugging-port={CDP_PORT}",
                f"--user-data-dir={str(self.profile_dir)}",
                "--no-first-run",
                "--no-default-browser-check",
                target_url
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(25):
                time.sleep(0.4)
                if self.is_chrome_running():
                    break
        else:
            from playwright.sync_api import sync_playwright
            try:
                with sync_playwright() as p:
                    browser = p.chromium.connect_over_cdp(CDP_URL)
                    context = browser.contexts[0] if browser.contexts else browser.new_context()
                    page = context.pages[0] if context.pages else context.new_page()
                    if "flow.google.com" not in page.url and "labs.google/fx" not in page.url:
                        page.goto(target_url)
            except Exception:
                pass

    def open_chrome_for_login(self):
        """Tek tıkla Chrome'u doğrudan Google Flow ile açar."""
        self.start_chrome_daemon("https://flow.google.com/")

    def get_flow_credit_balance(self) -> Optional[int]:
        """Google Flow'daki kalan krediyi okur."""
        if not self.is_chrome_running():
            return None
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(CDP_URL)
                context = browser.contexts[0] if browser.contexts else None
                if not context or not context.pages:
                    return None
                page = context.pages[0]

                # Menü zaten açıksa kontrol et
                cred_el = page.locator("text=/\\d+\\s+Google Flow kredi/").first
                if not cred_el.is_visible():
                    pro_badge = page.locator(".tier-chip").first
                    if not pro_badge.is_visible():
                        pro_badge = page.get_by_text("PRO", exact=True).first
                    if pro_badge.is_visible():
                        pro_badge.click(timeout=1500)
                        time.sleep(0.5)

                cred_el = page.locator("text=/\\d+\\s+Google Flow kredi/").first
                credit_val = None
                if cred_el.is_visible():
                    txt = cred_el.inner_text()
                    match = re.search(r"(\d+)", txt)
                    if match:
                        credit_val = int(match.group(1))

                # Menüyü kesinlikle kapat (case-insensitive ve doğrudan buton tıklaması)
                try:
                    close_btn = page.locator('button[aria-label*="kapat" i], button[aria-label*="close" i], .cdk-overlay-container button:has-text("close")').first
                    if close_btn.is_visible():
                        close_btn.click()
                        time.sleep(0.3)
                except Exception:
                    pass

                page.evaluate('''() => {
                    document.querySelectorAll('.cdk-overlay-backdrop').forEach(b => b.click());
                    document.querySelectorAll('button[aria-label*="kapat" i], button[aria-label*="close" i]').forEach(b => b.click());
                }''')
                page.keyboard.press("Escape")
                time.sleep(0.4)
                return credit_val
        except Exception as e:
            print(f"[FlowCDPBot] Kredi okuma hatası: {e}")
        return None

    def generate_flow_video_full_auto(
        self,
        topic: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Google Flow üzerinden Veo 3.1 3D videoyu %100 otonom üretir:
        1. Promptu girer ve gönderir.
        2. Çıkan 'Onayla ve bir daha sorma' butonuna DOĞRUDAN mouse ile tıklar.
        3. Eski videoları hafızaya alır, ASLA eski videoyu tekrar indirmez!
        4. Render sürecini WebGL/Resource Timing üzerinden canlı takip eder.
        5. Yeni videoyu doğrudan Google CDN üzerinden çekip 9:16 + ASMR müzikle montajlar.
        """
        from playwright.sync_api import sync_playwright

        video_id = f"short_{int(time.time())}"
        work_dir = Path(CANDIDATES_DIR) / video_id
        work_dir.mkdir(parents=True, exist_ok=True)
        raw_video = work_dir / "flow_generated.mp4"

        if progress_callback:
            progress_callback(0.08, "1/4 • AI Sentezi", "Gemini 3.6 ile tamamen özgün viral 3D Pixar senaryosu hazırlanıyor...")

        p_data = self.prompter.generate_master_prompt(topic)
        prompt = p_data["master_video_prompt"]
        title = p_data.get("title", "Cute 3D Pixar Animation! ✨ #Shorts")
        description = p_data.get("description", "Low stimulation 3D animation for kids. #Shorts #Cute #Pixar3D")
        tags = p_data.get("tags", ["Shorts", "3DAnimation", "Pixar", "LowStimulation", "Cute", "Relaxing"])
        theme = p_data.get("theme", "Google Flow Veo 3.1")

        if progress_callback:
            progress_callback(0.18, "2/4 • Google Flow Oturumu", "Chrome Google Flow stüdyosuna bağlanılıyor...")

        self.start_chrome_daemon("https://flow.google.com/")

        download_success = False

        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp(CDP_URL)
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()

                # Flow çalışma alanında değilsek git
                if "flow.google.com" not in page.url and "labs.google/fx" not in page.url:
                    page.goto("https://flow.google.com/", timeout=45000)
                    time.sleep(2)

                # Ana sayfadaysak '+ Yeni proje' butonuna tıkla
                for proj_btn in [
                    "text='Yeni proje'",
                    "button:has-text('Yeni proje')",
                    "button:has-text('New project')",
                    "button:has-text('Create with Google Flow')"
                ]:
                    try:
                        btn = page.locator(proj_btn).first
                        if btn.is_visible():
                            btn.click()
                            time.sleep(2)
                            break
                    except Exception:
                        pass

                # Herhangi bir iOS veya duyuru popup'ı varsa kapat
                for pop_sel in [
                    "button:has-text('Başlayın')",
                    "button:has-text('Get started')",
                    "button:has-text('Dismiss')",
                    "button:has-text('Anladım')",
                    "button[aria-label*='Kapat']",
                    "button[aria-label*='Close']"
                ]:
                    try:
                        pbtn = page.locator(pop_sel).first
                        if pbtn.is_visible():
                            pbtn.click()
                            time.sleep(1)
                    except Exception:
                        pass
                page.keyboard.press("Escape")

                # Sayfadaki tüm mevcut video ve CDN kaynak URL'lerinin fotoğrafını çek
                initial_video_urls = page.evaluate('''() => {
                    const urls = new Set();
                    try {
                        performance.getEntriesByType('resource').forEach(r => {
                            if (r.name && (r.name.includes('/video/') || r.name.includes('getMediaUrlRedirect'))) {
                                urls.add(r.name);
                            }
                        });
                    } catch(e) {}
                    document.querySelectorAll('video, source, [src*="getMediaUrlRedirect"], [src*="/video/"]').forEach(el => {
                        const s = el.src || el.currentSrc || el.getAttribute('src');
                        if (s) urls.add(s);
                    });
                    return Array.from(urls);
                }''')
                print(f"[FlowCDPBot] Başlangıçtaki mevcut video/kaynak sayısı: {len(initial_video_urls)}")

                if progress_callback:
                    progress_callback(0.28, "2/4 • Prompt İletimi", f"Google Flow'a yeni senaryo gönderiliyor: '{title[:35]}...'")

                # Prompt kutusunu bul ve temizle
                prompt_box = page.locator("div[contenteditable='true']").last
                prompt_box.wait_for(state="visible", timeout=30000)
                prompt_box.click()
                time.sleep(0.3)

                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                time.sleep(0.3)

                # Promptu klavyeyle yaz
                page.keyboard.type(prompt, delay=5)
                time.sleep(1)

                # Promptu gönder (Önce submit butonunu tıkla, yoksa Enter bas)
                try:
                    submit_btn = page.locator('button[aria-label="Oluşturmaya başla"], button.generate-icon-button, button:has(mat-icon:has-text("arrow_forward"))').first
                    if submit_btn.is_visible():
                        submit_btn.click()
                        time.sleep(1.5)
                    else:
                        page.keyboard.press("Enter")
                        time.sleep(1.5)
                except Exception:
                    page.keyboard.press("Enter")
                    time.sleep(1.5)

                if progress_callback:
                    progress_callback(0.38, "3/4 • Akıllı Onay", "Kredi onayı kontrol ediliyor ve otomatik tıklanıyor...")

                # Kredi Onayı Butonuna Tıkla ("Onayla ve bir daha sorma" veya "Onayla")
                for _ in range(15):
                    try:
                        btn_always = page.get_by_text("Onayla ve bir daha sorma", exact=False).last
                        btn_her_zaman = page.get_by_text("Her zaman onayla", exact=False).last
                        btn_onayla = page.get_by_text("Onayla", exact=True).last

                        if btn_always.count() > 0 and btn_always.is_visible():
                            btn_always.click()
                            print("[FlowCDPBot] 'Onayla ve bir daha sorma' butonu tıklandı!")
                            time.sleep(2)
                            break
                        elif btn_her_zaman.count() > 0 and btn_her_zaman.is_visible():
                            btn_her_zaman.click()
                            print("[FlowCDPBot] 'Her zaman onayla' butonu tıklandı!")
                            time.sleep(2)
                            break
                        elif btn_onayla.count() > 0 and btn_onayla.is_visible():
                            btn_onayla.click()
                            print("[FlowCDPBot] 'Onayla' butonu tıklandı!")
                            time.sleep(2)
                            break
                    except Exception:
                        pass
                    time.sleep(1)

                if progress_callback:
                    progress_callback(0.42, "3/4 • Veo 3.1 Render", "Veo 3.1 video render işlemi başladı (%0)...")

                # RENDER VE YENİ VİDEO YAKALAMA DÖNGÜSÜ (Maksimum 4.5 dakika)
                start_render_time = time.time()
                for step in range(95):
                    time.sleep(2.5)
                    elapsed = time.time() - start_render_time

                    # 1. Canlı Render Yüzdesi ve Dinamik İlerleme Hesaplama
                    dom_pct = page.evaluate(r'''() => {
                        // A. En baştaki (en yeni) tile'ın progress-bar stiline bak
                        const firstTile = document.querySelector('flow-grid-tile-container');
                        if (firstTile) {
                            const pbar = firstTile.querySelector('.progress-bar');
                            if (pbar) {
                                const style = pbar.getAttribute('style') || '';
                                const match = style.match(/--progress-percent:\s*(\d+)%/);
                                if (match) return parseInt(match[1]);
                            }
                        }
                        // B. Metin içinde %XX veya XX% arama (Türkçe '%21' veya İngilizce '21%')
                        const texts = Array.from(document.querySelectorAll('*'))
                            .map(e => e.textContent ? e.textContent.trim() : '')
                            .filter(t => /^%?\d{1,3}%?$/.test(t) && t.includes('%'));
                        if (texts.length > 0) {
                            const raw = texts[0].replace('%', '').trim();
                            const val = parseInt(raw);
                            if (!isNaN(val)) return val;
                        }
                        return null;
                    }''')

                    # Dinamik süre tabanlı ilerleme (Veo 3.1 ortalama 55-65 sn sürer)
                    # 42%'den 86%'ya kadar düzenli, akıcı bir şekilde artar (asla ekranda donup kalmaz!)
                    time_pct = min(86, int(42 + (elapsed / 60.0) * 44))
                    current_display_pct = max(time_pct, dom_pct if dom_pct is not None else 0)
                    prog_ratio = current_display_pct / 100.0

                    if progress_callback:
                        progress_callback(
                            prog_ratio,
                            "3/4 • Veo 3.1 Render",
                            f"3D Video Render Ediliyor: %{current_display_pct} (Geçen süre: {int(elapsed)} sn)..."
                        )

                    # 2. En yeni tile'ı hover et (video oynatıcıyı ve CDN akışını tetikler)
                    try:
                        first_tile = page.locator("flow-grid-tile-container").first
                        if first_tile.is_visible():
                            first_tile.hover()
                    except Exception:
                        pass

                    # 3. YENİ VİDEO URL'SİNİ BUL (DOM Video, Thumbnail Dönüşümü veya Performance Timing)
                    v_url = page.evaluate('''([existingUrls]) => {
                        // Kaynak A: En baştaki yeni tile'ın içindeki video elementi
                        const firstTile = document.querySelector('flow-grid-tile-container');
                        if (firstTile) {
                            const v = firstTile.querySelector('video');
                            if (v) {
                                const s = v.currentSrc || v.src;
                                if (s && !existingUrls.includes(s) && !s.includes('placeholder')) return s;
                            }
                            // Kaynak B: En baştaki yeni tile'ın görselinden video URL türetme (/image/ -> /video/)
                            const img = firstTile.querySelector('img.thumbnail');
                            if (img && img.src && img.src.includes('flow-content.google/image/')) {
                                const derived = img.src.replace('/image/', '/video/');
                                if (!existingUrls.includes(derived)) return derived;
                            }
                        }

                        // Kaynak C: Performance Resource Timing (En son yüklenen video kaynakları)
                        try {
                            const entries = performance.getEntriesByType('resource');
                            for (let i = entries.length - 1; i >= 0; i--) {
                                const name = entries[i].name;
                                if (name && (name.includes('/video/') || name.includes('getMediaUrlRedirect'))) {
                                    if (!existingUrls.includes(name) && !name.includes('placeholder')) {
                                        return name;
                                    }
                                }
                            }
                        } catch(e) {}

                        // Kaynak D: DOM'daki tüm video elementleri
                        const vids = Array.from(document.querySelectorAll('video'));
                        for (let i = 0; i < vids.length; i++) {
                            const v = vids[i];
                            const src = v.currentSrc || (v.querySelector('source') ? v.querySelector('source').src : null) || v.src;
                            if (src && !existingUrls.includes(src) && !src.includes('placeholder')) {
                                return src;
                            }
                        }
                        return null;
                    }''', [initial_video_urls])

                    if v_url and elapsed > 8:
                        print(f"[FlowCDPBot] YENİ Video URL yakalandı: {v_url[:75]}")
                        if progress_callback:
                            progress_callback(0.88, "4/4 • Ultra-Hızlı İndirme", "Render Tamamlandı! Yeni video Google CDN üzerinden doğrudan çekiliyor...")

                        resp = page.request.get(v_url)
                        if resp.status == 200 and len(resp.body()) > 50000:
                            with open(raw_video, "wb") as f:
                                f.write(resp.body())
                            print(f"[FlowCDPBot] Yeni video başarıyla indirildi: {raw_video.stat().st_size} bytes")
                            download_success = True
                            break

            except Exception as e:
                print(f"[FlowCDPBot] Akış hatası: {e}")

        if not raw_video.exists() or raw_video.stat().st_size < 1000:
            raise RuntimeError("Google Flow'dan yeni video henüz indirilemedi. Lütfen renderın %100 tamamlanmasını bekleyin!")

        if progress_callback:
            progress_callback(0.92, "4/4 • ASMR Montajı", "1080x1920 9:16 dikey format ve sakinleştirici çocuk ASMR müziği miksleniyor...")

        # Post-Production (1080x1920 + ASMR Müzik + Kapak Görseli + Metadata)
        meta = self.enhancer.process_and_import_video(
            raw_video_path=str(raw_video),
            title=title,
            description=description,
            tags=tags,
            theme=theme
        )

        if progress_callback:
            progress_callback(1.0, "Tamamlandı!", f"Tebrikler! '{title}' videosu stüdyoya eklendi.")

        return meta
