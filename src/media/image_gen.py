import urllib.parse
import requests
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import time
import random


class ImageGenerator:
    def __init__(self):
        pass

    def generate_scene_image(
        self,
        prompt: str,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
        seed: Optional[int] = None
    ) -> str:
        """
        Pollinations / Flux uç noktalarından yüksek kaliteli 9:16 sahne görseli üretir.
        """
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        used_seed = seed if seed is not None else random.randint(10000, 99999)

        # Görsel motorunun hızlı ve kaliteli üretmesi için prompt'u optimize et
        clean_prompt = " ".join(prompt.split())[:180]
        encoded_prompt = urllib.parse.quote(clean_prompt)
        
        # 1. Öncelik: 768x1344 (Çok daha hızlı render olur, ardından 1080x1920 Lanczos upscale edilir)
        urls = [
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1344&nologo=true&seed={used_seed}",
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={used_seed}"
        ]

        for url in urls:
            for attempt in range(2):
                try:
                    response = requests.get(url, timeout=14)
                    if response.status_code == 200 and len(response.content) > 4000:
                        with open(target_path, "wb") as f:
                            f.write(response.content)
                        
                        # Tam 1080x1920 boyutlandırma ve netlik
                        with Image.open(target_path) as img:
                            if img.size != (width, height):
                                img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
                                img_resized.save(target_path, format="JPEG", quality=95)
                        return str(target_path)
                except Exception as e:
                    time.sleep(0.5)

        # Yedek görsel motoru
        print("[ImageGenerator] Servis yoğun, dinamik çizgi görseli üretildi.")
        self._create_fallback_image(target_path, prompt, width, height)
        return str(target_path)

    def _create_fallback_image(self, target_path: Path, prompt: str, width: int, height: int):
        """Ağ gecikmelerinde render sürecinin aksamaması için estetik arka plan ve sevimli karakter silüeti çizer."""
        img = Image.new("RGB", (width, height), color=(25, 20, 45))
        draw = ImageDraw.Draw(img)

        # Gradyan gökyüzü
        c1 = (random.randint(50, 100), random.randint(20, 70), random.randint(120, 220))
        c2 = (random.randint(220, 255), random.randint(130, 200), random.randint(90, 160))
        for y in range(height):
            r = int(c1[0] + (c2[0] - c1[0]) * (y / height))
            g = int(c1[1] + (c2[1] - c1[1]) * (y / height))
            b = int(c1[2] + (c2[2] - c1[2]) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Işıltılar
        for _ in range(40):
            x = random.randint(0, width)
            y = random.randint(0, height)
            rad = random.randint(8, 60)
            draw.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(255, 255, 255))

        # Sevimli merkez figür
        center_x, center_y = width // 2, height // 2
        body_radius = 260
        draw.ellipse(
            [center_x - body_radius, center_y - body_radius + 40, center_x + body_radius, center_y + body_radius + 40],
            fill=(255, 150, 30)
        )
        draw.ellipse([center_x - 110, center_y - 70, center_x - 20, center_y + 20], fill=(255, 255, 255))
        draw.ellipse([center_x + 20, center_y - 70, center_x + 110, center_y + 20], fill=(255, 255, 255))
        draw.ellipse([center_x - 65, center_y - 45, center_x - 35, center_y - 15], fill=(0, 0, 0))
        draw.ellipse([center_x + 35, center_y - 45, center_x + 65, center_y - 15], fill=(0, 0, 0))
        draw.arc([center_x - 70, center_y, center_x + 70, center_y + 70], start=0, end=180, fill=(0, 0, 0), width=10)

        img.save(target_path, format="JPEG", quality=92)
