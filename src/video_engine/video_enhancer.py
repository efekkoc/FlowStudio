import os
import time
import uuid
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import imageio_ffmpeg

from config.settings import CANDIDATES_DIR, MUSIC_DIR, SFX_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS


class VideoEnhancer:
    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.music_dir = Path(MUSIC_DIR)
        self.sfx_dir = Path(SFX_DIR)

    def process_and_import_video(
        self,
        raw_video_path: str,
        title: str,
        description: str,
        tags: list,
        theme: str = "Google Labs 3D Animation",
        music_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Google Labs / Veo'dan indirilen ham videoyu alır:
        - 1080x1920 9:16 dikey formata dönüştürür.
        - Arka plana büyüleyici, sakinleştirici / ASMR çocuk müziği ve ses efektleri giydirir.
        - Kapak görselini ve YouTube metadata'sını oluşturup stüdyo aday listesine ekler.
        """
        video_id = f"short_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        work_dir = Path(CANDIDATES_DIR) / video_id
        work_dir.mkdir(parents=True, exist_ok=True)

        final_video_path = work_dir / "final_short.mp4"
        thumbnail_path = work_dir / "thumbnail.jpg"

        # 1. Ses / Müzik Seçimi
        selected_music = music_path or self._get_default_music()

        # 2. FFmpeg ile 1080x1920 Ölçekleme ve Müzik Miksleme
        inputs = ["-y", "-i", raw_video_path]
        filter_complex = f"[0:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1[vout]"

        if selected_music and os.path.exists(selected_music):
            inputs.extend(["-stream_loop", "-1", "-i", selected_music])
            # Hem videonun orijinal sesi (varsa) hem de arka plan müziğini yumuşak miksle
            filter_complex += ";[1:a]volume=0.35[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            cmd = [self.ffmpeg_exe] + inputs + [
                "-filter_complex", filter_complex,
                "-map", "[vout]", "-map", "[aout]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(final_video_path)
            ]
        else:
            cmd = [self.ffmpeg_exe] + inputs + [
                "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1",
                "-c:v", "libx264", "-c:a", "aac",
                str(final_video_path)
            ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            # Ses miksinde hata olursa sadece videoyu kopyala ve yeniden boyutlandır
            fallback_cmd = [
                self.ffmpeg_exe, "-y", "-i", raw_video_path,
                "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1",
                "-c:v", "libx264",
                str(final_video_path)
            ]
            subprocess.run(fallback_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 3. Kapak Görseli Çıkar (0.5 saniyedeki kare)
        cmd_thumb = [
            self.ffmpeg_exe, "-y", "-ss", "00:00:01.000",
            "-i", str(final_video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(thumbnail_path)
        ]
        try:
            subprocess.run(cmd_thumb, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        # 4. Metadata Kaydet
        metadata = {
            "video_id": video_id,
            "title": title,
            "description": description,
            "tags": tags,
            "theme": theme,
            "duration": self._get_duration(str(final_video_path)),
            "video_path": str(final_video_path),
            "thumbnail_path": str(thumbnail_path) if thumbnail_path.exists() else "",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending_review",
            "source": "Google Labs / Veo 3D AI Video"
        }

        with open(work_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata

    def _get_default_music(self) -> Optional[str]:
        files = list(self.music_dir.glob("*.mp3")) + list(self.music_dir.glob("*.wav"))
        return str(files[0]) if files else None

    def _get_duration(self, path: str) -> float:
        try:
            cmd = [self.ffmpeg_exe, "-i", path]
            res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            for line in res.stderr.split("\n"):
                if "Duration:" in line:
                    t_str = line.split("Duration:")[1].split(",")[0].strip()
                    h, m, s = t_str.split(":")
                    return float(h)*3600 + float(m)*60 + float(s)
        except Exception:
            pass
        return 25.0
