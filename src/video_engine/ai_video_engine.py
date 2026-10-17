import os
import time
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

from config.settings import BASE_DIR, CANDIDATES_DIR, VIDEO_WIDTH, VIDEO_HEIGHT
from src.generator.google_labs_prompter import GoogleLabsPrompter
from src.video_engine.video_enhancer import VideoEnhancer


class AIVideoEngine:
    def __init__(self):
        self.fal_key = os.getenv("FAL_KEY", "")
        self.enhancer = VideoEnhancer()
        self.prompter = GoogleLabsPrompter()

    def generate_autonomous_video(
        self,
        topic: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Kullanıcıdan sıfır girdi ile %100 otonom video üretimi:
        1. Gemini en viral 3D Pixar fikrini bulur.
        2. AI Video API'si veya sinematik video motoru ile videoyu doğrudan üretir.
        3. 1080x1920 yapar ve büyülü ASMR müzik ekler.
        4. Panele hazır video olarak ekler.
        """
        video_id = f"short_{int(time.time())}"
        work_dir = Path(CANDIDATES_DIR) / video_id
        work_dir.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(0.2, "1/4: Gemini 3.6 ile viral 3D konu ve master prompt üretiliyor...")

        p_data = self.prompter.generate_master_prompt(topic)
        prompt = p_data["master_video_prompt"]
        title = p_data.get("title", "Cute 3D Pixar Animation! 🐰✨ #Shorts")
        description = p_data.get("description", "Magical 3D animation. #Shorts #LowStimulation #Pixar3D")
        tags = p_data.get("tags", ["Shorts", "3DAnimation", "Pixar", "LowStimulation", "Cute", "Relaxing"])
        theme = p_data.get("theme", "3D Pixar Animation")

        raw_video = work_dir / "raw_video.mp4"

        if progress_callback:
            progress_callback(0.5, "2/4: Yapay zeka 3D video motoru çalışıyor (Kling / Wan 2.1 / LTX)...")

        # 1. Fal.ai / AI Video API Denemesi (Eğer FAL_KEY varsa)
        generated = False
        fal_api_key = os.getenv("FAL_KEY", "")
        if fal_api_key and len(fal_api_key) > 5:
            try:
                import fal_client
                os.environ["FAL_KEY"] = fal_api_key
                handler = fal_client.submit(
                    "fal-ai/ltx-video",
                    arguments={
                        "prompt": prompt[:250],
                        "aspect_ratio": "9:16"
                    }
                )
                res = handler.get()
                video_url = res["video"]["url"]
                r = requests.get(video_url, timeout=60)
                with open(raw_video, "wb") as f:
                    f.write(r.content)
                generated = True
            except Exception as e:
                print(f"[AIVideoEngine] Fal API hatası: {e}")

        # 2. Doğrudan Otonom 3D Video Montaj Motoru (API Olmasa Bile Çalışır)
        if not generated:
            self._render_cinematic_3d_video(prompt, raw_video)

        if progress_callback:
            progress_callback(0.8, "3/4: 1080x1920 9:16 formatı ve büyülü ASMR müzik miksleniyor...")

        # 3. Post-Production & Büyülü Müzik Giydirme
        meta = self.enhancer.process_and_import_video(
            raw_video_path=str(raw_video),
            title=title,
            description=description,
            tags=tags,
            theme=theme
        )

        if progress_callback:
            progress_callback(1.0, "4/4: Video başarıyla tamamlandı!")

        return meta

    def _render_cinematic_3d_video(self, prompt: str, output_path: Path):
        """
        Harici video API'si olmasa bile sıfır bekleme ile 1080x1920 3D Pixar
        hareketli video oluşturan yerel sinematik motor.
        """
        import imageio_ffmpeg
        import subprocess
        from src.media.image_gen import ImageGenerator

        img_gen = ImageGenerator()
        temp_img = output_path.parent / "scene_3d.jpg"
        
        # 3D Pixar sahnesi üret
        img_gen.generate_scene_image(
            prompt=f"{prompt[:160]}, 3D Disney Pixar movie render, Unreal Engine 5, 8k volumetric lighting, 9:16",
            output_path=str(temp_img),
            width=1080,
            height=1920
        )

        # 20 saniyelik sinematik 3D kamera hareketi (Dolly Zoom & Parallax)
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        duration = 20
        total_frames = duration * 30
        
        vf = (
            f"scale=8000:-1,"
            f"zoompan=z='min(1.28, 1.0 + (on/{total_frames})*0.28)':"
            f"x='iw/2-(iw/zoom/2) + sin(on*0.03)*30':"
            f"y='ih/2-(ih/zoom/2) + cos(on*0.025)*20':"
            f"d={total_frames}:s=1080x1920:fps=30"
        )

        cmd = [
            ffmpeg, "-y",
            "-loop", "1", "-i", str(temp_img),
            "-vf", vf,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-r", "30",
            str(output_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
