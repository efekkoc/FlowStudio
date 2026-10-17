import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

from config.settings import CANDIDATES_DIR, STYLE_PRESETS, VOICE_PRESETS
from src.generator.story_generator import StoryGenerator, VideoStory
from src.media.tts import TTSEngine
from src.media.image_gen import ImageGenerator
from src.media.audio_manager import AudioManager
from src.video_engine.subtitles import SubtitleEngine
from src.video_engine.renderer import VideoRenderer


class VideoPipeline:
    def __init__(self):
        self.story_gen = StoryGenerator()
        self.tts_engine = TTSEngine()
        self.img_gen = ImageGenerator()
        self.audio_mgr = AudioManager()
        self.subtitle_engine = SubtitleEngine()
        self.renderer = VideoRenderer()

    def generate_single_short(
        self,
        topic: Optional[str] = None,
        style_key: str = "pixar_3d",
        voice_id: str = "en-US-AnaNeural",
        num_scenes: int = 5,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Uçtan uca tek bir YouTube Shorts videosu üretir ve aday klasörüne kaydeder.
        """
        video_id = f"short_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        work_dir = Path(CANDIDATES_DIR) / video_id
        work_dir.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(0.1, "1/5: Fikir ve senaryo üretiliyor (Gemini)...")

        # 1. Aşama: Senaryo Üretimi
        story: VideoStory = self.story_gen.generate_story(
            topic=topic,
            style_key=style_key,
            num_scenes=num_scenes
        )

        all_word_timings = []
        scene_video_paths = []
        current_time_offset = 0.0

        if progress_callback:
            progress_callback(0.3, "2/5: Seslendirme ve kelime zamanlamaları hazırlanıyor (Edge-TTS)...")

        # 2 & 3. Aşama: Ses, Görsel ve Sahne Klipleri
        for i, scene in enumerate(story.scenes):
            scene_num = i + 1
            if progress_callback:
                progress_callback(0.3 + (i / len(story.scenes)) * 0.35, f"3/5: Sahne {scene_num}/{len(story.scenes)} üretiliyor...")

            # Ses Dosyası
            audio_file = work_dir / f"scene_{scene_num}_audio.mp3"
            tts_res = self.tts_engine.generate_speech(
                text=scene.narration,
                output_audio_path=str(audio_file),
                voice=voice_id
            )

            # Zaman damgalarını genel videoya göre ötele
            for wt in tts_res["word_timings"]:
                all_word_timings.append({
                    "word": wt["word"],
                    "start": wt["start"] + current_time_offset,
                    "end": wt["end"] + current_time_offset
                })
            current_time_offset += tts_res["duration"]

            # Görsel Dosyası
            image_file = work_dir / f"scene_{scene_num}_image.jpg"
            self.img_gen.generate_scene_image(
                prompt=scene.image_prompt,
                output_path=str(image_file),
                width=1080,
                height=1920
            )

            # Ses Efekti (SFX)
            sfx_path = self.audio_mgr.get_sfx(scene.sfx_keyword or "pop")

            # Sahne Render
            scene_clip = work_dir / f"scene_{scene_num}_clip.mp4"
            self.renderer.render_scene_clip(
                image_path=str(image_file),
                audio_path=str(audio_file),
                output_scene_path=str(scene_clip),
                camera_motion=scene.camera_motion or "rapid_zoom_in",
                sfx_path=sfx_path,
                emoji_overlay=getattr(scene, "emoji_overlay", "✨")
            )
            scene_video_paths.append(str(scene_clip))

        if progress_callback:
            progress_callback(0.75, "4/5: Animasyonlu altyazılar oluşturuluyor...")

        # 4. Aşama: Altyazı Üretimi
        ass_file = work_dir / "subtitles.ass"
        self.subtitle_engine.create_ass_subtitles(
            word_timings=all_word_timings,
            output_ass_path=str(ass_file)
        )

        if progress_callback:
            progress_callback(0.85, "5/5: Müzik miksleniyor ve nihai Shorts render ediliyor...")

        # 5. Aşama: Nihai Video Render
        final_video = work_dir / "final_short.mp4"
        bg_music = self.audio_mgr.get_background_music()

        self.renderer.concatenate_scenes_and_finish(
            scene_video_paths=scene_video_paths,
            output_final_path=str(final_video),
            bg_music_path=bg_music,
            ass_subtitle_path=str(ass_file)
        )

        # Kapak görseli (Sahne 1 görseli)
        thumbnail_path = work_dir / "thumbnail.jpg"
        if (work_dir / "scene_1_image.jpg").exists():
            import shutil
            shutil.copy(str(work_dir / "scene_1_image.jpg"), str(thumbnail_path))

        # Metadata Dosyası
        metadata = {
            "video_id": video_id,
            "title": story.title,
            "description": story.description,
            "tags": story.tags,
            "theme": story.theme,
            "duration": current_time_offset,
            "video_path": str(final_video),
            "thumbnail_path": str(thumbnail_path),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending_review",
            "scenes": [s.dict() for s in story.scenes]
        }

        meta_file = work_dir / "metadata.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        if progress_callback:
            progress_callback(1.0, "Tamamlandı! Video aday listesine eklendi.")

        return metadata
