import os
import time
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

from config.settings import BASE_DIR, CANDIDATES_DIR
from src.generator.google_labs_prompter import GoogleLabsPrompter
from src.video_engine.video_enhancer import VideoEnhancer


class DirectVideoAPIClient:
    def __init__(self):
        self.useapi_token = os.getenv("USEAPI_TOKEN", "")
        self.fal_key = os.getenv("FAL_KEY", "")
        self.enhancer = VideoEnhancer()
        self.prompter = GoogleLabsPrompter()

    def generate_full_auto_video(
        self,
        topic: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Sıfır tarayıcı, sıfır kopyala-yapıştır:
        1. Gemini 3.6 viral 3D Pixar fikrini bulur.
        2. Google Flow (useapi.net) veya Fal.ai Video API'si ile videoyu doğrudan arka planda üretir.
        3. 1080x1920 yapar ve büyülü ASMR fon müziği ekler.
        4. YouTube aday listesine hazır olarak koyar.
        """
        video_id = f"short_{int(time.time())}"
        work_dir = Path(CANDIDATES_DIR) / video_id
        work_dir.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(0.15, "1/4: Gemini 3.6 Flash ile viral 3D konu ve master prompt üretiliyor...")

        p_data = self.prompter.generate_master_prompt(topic)
        prompt = p_data["master_video_prompt"]
        title = p_data.get("title", "Cute 3D Pixar Animation! 🐰✨ #Shorts")
        description = p_data.get("description", "Magical 3D animation. #Shorts #LowStimulation #Pixar3D")
        tags = p_data.get("tags", ["Shorts", "3DAnimation", "Pixar", "LowStimulation", "Cute", "Relaxing"])
        theme = p_data.get("theme", "3D Pixar Animation")

        raw_video = work_dir / "raw_generated.mp4"

        if progress_callback:
            progress_callback(0.40, "2/4: Video API'si çağrılıyor (Google Flow / Veo 3.1)...")

        # 1. Öncelik: useapi.net Google Flow API (Veo 3.1)
        video_url = None
        useapi_tok = os.getenv("USEAPI_TOKEN", self.useapi_token)
        if useapi_tok and len(useapi_tok.strip()) > 5:
            try:
                headers = {"Authorization": f"Bearer {useapi_tok}", "Content-Type": "application/json"}
                payload = {
                    "prompt": prompt,
                    "aspect_ratio": "9:16",
                    "model": "veo-3.1"
                }
                resp = requests.post("https://api.useapi.net/v1/google-flow/videos", json=payload, headers=headers, timeout=30)
                if resp.status_code in [200, 201, 202]:
                    job = resp.json()
                    job_id = job.get("job_id") or job.get("id")
                    # Polling
                    for _ in range(60):
                        time.sleep(4)
                        st_resp = requests.get(f"https://api.useapi.net/v1/google-flow/jobs/{job_id}", headers=headers, timeout=20)
                        if st_resp.status_code == 200:
                            st_data = st_resp.json()
                            if st_data.get("status") == "completed" or st_data.get("video_url"):
                                video_url = st_data.get("video_url") or st_data.get("output", {}).get("video")
                                break
            except Exception as e:
                print(f"[DirectVideoAPI] useapi Google Flow hatası: {e}")

        # 2. Öncelik: Fal.ai Video API (Kling / LTX / Wan 2.1)
        fal_k = os.getenv("FAL_KEY", self.fal_key)
        if not video_url and fal_k and len(fal_k.strip()) > 5:
            try:
                import fal_client
                os.environ["FAL_KEY"] = fal_k
                handler = fal_client.submit(
                    "fal-ai/ltx-video",
                    arguments={"prompt": prompt[:250], "aspect_ratio": "9:16"}
                )
                res = handler.get()
                video_url = res.get("video", {}).get("url")
            except Exception as e:
                print(f"[DirectVideoAPI] Fal.ai hatası: {e}")

        # Videoyu indir
        if video_url:
            r = requests.get(video_url, timeout=60)
            with open(raw_video, "wb") as f:
                f.write(r.content)
        else:
            # Fallback
            self._render_placeholder_video(prompt, raw_video)

        if progress_callback:
            progress_callback(0.80, "3/4: 1080x1920 9:16 formatı ve büyülü ASMR müzik miksleniyor...")

        # 3. Post-Production
        meta = self.enhancer.process_and_import_video(
            raw_video_path=str(raw_video),
            title=title,
            description=description,
            tags=tags,
            theme=theme
        )

        if progress_callback:
            progress_callback(1.0, "4/4: Video başarıyla hazırlandı!")

        return meta

    def _render_placeholder_video(self, prompt: str, output_path: Path):
        import imageio_ffmpeg
        import subprocess
        from src.media.image_gen import ImageGenerator
        img_gen = ImageGenerator()
        temp_img = output_path.parent / "scene_3d.jpg"
        img_gen.generate_scene_image(
            prompt=f"{prompt[:160]}, 3D Disney Pixar movie render, 9:16 vertical",
            output_path=str(temp_img),
            width=1080,
            height=1920
        )
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg, "-y",
            "-loop", "1", "-i", str(temp_img),
            "-vf", "scale=1080:1920,zoompan=z='min(1.2, 1.0+on*0.001)':d=600:s=1080x1920:fps=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-t", "20",
            str(output_path)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
