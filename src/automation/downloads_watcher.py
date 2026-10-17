import os
import time
import shutil
import threading
from pathlib import Path
from typing import Optional, Callable

from config.settings import CANDIDATES_DIR, BASE_DIR
from src.generator.google_labs_prompter import GoogleLabsPrompter
from src.video_engine.video_enhancer import VideoEnhancer


class DownloadsWatcher:
    def __init__(self, downloads_dir: Optional[str] = None):
        self.downloads_dir = Path(downloads_dir or os.path.expanduser("~/Downloads"))
        self.enhancer = VideoEnhancer()
        self.prompter = GoogleLabsPrompter()
        self.processed_files = set()
        self.is_running = False
        self._thread = None

        # Mevcut dosyaları kaydet (eski dosyaları tekrar işlememek için)
        if self.downloads_dir.exists():
            for f in self.downloads_dir.glob("*.mp4"):
                self.processed_files.add(f.name)

    def start(self, on_video_processed: Optional[Callable] = None):
        """Arka planda İndirilenler klasörünü dinlemeye başlar."""
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._watch_loop, args=(on_video_processed,), daemon=True)
        self._thread.start()
        print(f"[DownloadsWatcher] İndirilenler klasörü ({self.downloads_dir}) izleniyor...")

    def stop(self):
        self.is_running = False

    def _watch_loop(self, on_video_processed: Optional[Callable]):
        while self.is_running:
            try:
                if self.downloads_dir.exists():
                    video_files = list(self.downloads_dir.glob("*.mp4")) + list(self.downloads_dir.glob("*.webm"))
                    for vf in video_files:
                        # Dosya adı daha önce işlenmediyse ve dosya indirmesi tamamlandıysa (>100KB ve boyutu sabit)
                        if vf.name not in self.processed_files and not vf.name.endswith(".crdownload"):
                            initial_size = vf.stat().st_size
                            if initial_size > 100_000:
                                time.sleep(1.5)
                                # Boyut değişmediyse indirme bitmiştir
                                if vf.exists() and vf.stat().st_size == initial_size:
                                    print(f"[DownloadsWatcher] Yeni Google Labs videosu yakalandı: {vf.name}")
                                    self.processed_files.add(vf.name)
                                    self._process_downloaded_video(vf, on_video_processed)
            except Exception as e:
                print(f"[DownloadsWatcher] İzleme hatası: {e}")
            time.sleep(2)

    def _process_downloaded_video(self, video_file: Path, callback: Optional[Callable]):
        """Yeni inen videoya otomatik müzik giydirir ve YouTube metinlerini oluşturur."""
        try:
            p_data = self.prompter.generate_master_prompt()
            title = p_data.get("title", f"Cute 3D Pixar Shorts #{int(time.time()) % 1000} 🐰✨")
            description = p_data.get("description", "Magical 3D animation for kids. #Shorts #LowStimulation #Cute #Pixar3D")
            tags = p_data.get("tags", ["Shorts", "3DAnimation", "Pixar", "LowStimulation", "Cute", "Relaxing"])
            theme = p_data.get("theme", "Google Labs 3D Animation")

            meta = self.enhancer.process_and_import_video(
                raw_video_path=str(video_file),
                title=title,
                description=description,
                tags=tags,
                theme=theme
            )
            print(f"[DownloadsWatcher] Video başarıyla işlendi ve panele eklendi: {meta['title']}")
            if callback:
                callback(meta)
        except Exception as ex:
            print(f"[DownloadsWatcher] Video işleme hatası: {ex}")
