import os
import subprocess
import shutil
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from config.settings import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, FONTS_DIR


class VideoRenderer:
    def __init__(self):
        self.ffmpeg_exe = self._get_ffmpeg_path()
        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT
        self.fps = VIDEO_FPS

    def _get_ffmpeg_path(self) -> str:
        """Kullanılabilir en iyi FFmpeg ikili yolunu tespit eder."""
        try:
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            return shutil.which("ffmpeg") or "ffmpeg"

    def render_scene_clip(
        self,
        image_path: str,
        audio_path: str,
        output_scene_path: str,
        camera_motion: str = "rapid_zoom_in",
        sfx_path: Optional[str] = None,
        emoji_overlay: Optional[str] = None
    ) -> str:
        """
        Dinamik kamera hareketi (Punch zoom, Screen shake, Whip pan),
        zıplayan emoji çıkartması ve ses efektleriyle hareketli sahne klibi üretir.
        """
        out_p = Path(output_scene_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        duration = self._get_audio_duration(audio_path)
        if duration <= 0:
            duration = 3.0

        total_frames = int(duration * self.fps) + 5

        # 1. Aşama: Kamera Hareketi Filtresi (Ken Burns & Yüksek Dinamizm)
        if camera_motion == "screen_shake":
            # Aksiyon anında ekran sallantısı (deprem / kaos efekti)
            vf_filter = (
                f"scale=8000:-1,"
                f"zoompan=z=1.18:"
                f"x='iw/2-(iw/zoom/2) + sin(on*1.8)*22':"
                f"y='ih/2-(ih/zoom/2) + cos(on*2.1)*22':"
                f"d={total_frames}:s={self.width}x{self.height}:fps={self.fps}"
            )
        elif camera_motion == "punch_zoom":
            # Ani vuruş / zıplama zoom'u (1.0 -> 1.3 hızla patlayıp hafif süzülme)
            vf_filter = (
                f"scale=8000:-1,"
                f"zoompan=z='if(lte(on,15), 1.0 + (on/15)*0.28, 1.28 + sin((on-15)*0.1)*0.03)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={total_frames}:s={self.width}x{self.height}:fps={self.fps}"
            )
        elif camera_motion == "rapid_zoom_out":
            # Geriye hızlı açılma
            vf_filter = (
                f"scale=8000:-1,"
                f"zoompan=z='max(1.02, 1.30 - (on/{total_frames})*0.28)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={total_frames}:s={self.width}x{self.height}:fps={self.fps}"
            )
        elif camera_motion == "whip_pan_right":
            # Sağa hızlı kayma
            vf_filter = (
                f"scale=8000:-1,"
                f"zoompan=z=1.22:"
                f"x='min(iw-iw/zoom, (on/{total_frames})*(iw-iw/zoom))':"
                f"y='ih/2-(ih/zoom/2)':"
                f"d={total_frames}:s={self.width}x{self.height}:fps={self.fps}"
            )
        else:  # rapid_zoom_in (varsayılan)
            # İleriye akıcı ve enerjik yaklaşma
            vf_filter = (
                f"scale=8000:-1,"
                f"zoompan=z='min(1.32, 1.0 + (on/{total_frames})*0.32)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={total_frames}:s={self.width}x{self.height}:fps={self.fps}"
            )

        # 2. Aşama: Emoji Katmanı Hazırlığı (Opsiyonel)
        emoji_img_path = None
        if emoji_overlay:
            emoji_img_path = out_p.parent / f"{out_p.stem}_emoji.png"
            self._create_emoji_sticker(emoji_overlay, emoji_img_path)

        # FFmpeg Filtre Zinciri
        inputs = ["-y", "-loop", "1", "-i", image_path]
        filter_parts = [f"[0:v]{vf_filter}[bg_motion]"]
        final_video_label = "[bg_motion]"

        if emoji_img_path and emoji_img_path.exists():
            inputs.extend(["-i", str(emoji_img_path)])
            # Emoji ekranın sağ üstünde tatlı bir şekilde zıplayarak belirir
            overlay_expr = (
                f"[bg_motion][1:v]overlay=x='W-w-60':y='180 + sin(t*6)*15':"
                f"enable='between(t, 0.2, {duration - 0.2})'[v_with_emoji]"
            )
            filter_parts.append(overlay_expr)
            final_video_label = "[v_with_emoji]"

        # Ses ve SFX miksajı
        audio_idx = 2 if (emoji_img_path and emoji_img_path.exists()) else 1
        inputs.extend(["-i", audio_path])

        if sfx_path and os.path.exists(sfx_path):
            sfx_idx = audio_idx + 1
            inputs.extend(["-i", sfx_path])
            filter_parts.append(
                f"[{audio_idx}:a][{sfx_idx}:a]amix=inputs=2:duration=first:weights=1.0 0.55[a_out]"
            )
            audio_label = "[a_out]"
        else:
            audio_label = f"[{audio_idx}:a]"

        filter_complex = ";".join(filter_parts)

        cmd = [self.ffmpeg_exe] + inputs + [
            "-filter_complex", filter_complex,
            "-map", final_video_label,
            "-map", audio_label,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-r", str(self.fps),
            "-shortest",
            str(out_p)
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(out_p)

    def concatenate_scenes_and_finish(
        self,
        scene_video_paths: List[str],
        output_final_path: str,
        bg_music_path: Optional[str] = None,
        ass_subtitle_path: Optional[str] = None
    ) -> str:
        """Sahneleri akıcı geçişlerle bağlar, dinamik altyazıları ve arka plan müziğini gömer."""
        final_p = Path(output_final_path)
        final_p.parent.mkdir(parents=True, exist_ok=True)

        concat_list_file = final_p.parent / "concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for p in scene_video_paths:
                f.write(f"file '{Path(p).resolve()}'\n")

        merged_temp = final_p.parent / "merged_temp.mp4"

        # Sahneleri birleştir
        cmd_concat = [
            self.ffmpeg_exe, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c", "copy",
            str(merged_temp)
        ]
        subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        total_duration = self._get_video_duration(str(merged_temp))

        inputs = ["-i", str(merged_temp)]
        filter_complex = []
        audio_inputs = "[0:a]"

        # Arka plan müziği miksajı
        if bg_music_path and os.path.exists(bg_music_path):
            inputs.extend(["-stream_loop", "-1", "-i", bg_music_path])
            filter_complex.append(
                f"[1:a]volume=0.14[bg];{audio_inputs}[bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            audio_maps = ["-map", "0:v", "-map", "[aout]"]
        else:
            audio_maps = ["-map", "0:v", "-map", "0:a"]

        video_filters = []
        if ass_subtitle_path and os.path.exists(ass_subtitle_path):
            safe_ass = str(Path(ass_subtitle_path).resolve()).replace(":", "\\:").replace("'", "\\'")
            video_filters.append(f"subtitles='{safe_ass}'")

        cmd_final = [self.ffmpeg_exe, "-y"] + inputs

        if filter_complex and video_filters:
            cmd_final.extend([
                "-filter_complex", f"[0:v]{','.join(video_filters)}[vout];{filter_complex[0]}",
                "-map", "[vout]", "-map", "[aout]"
            ])
        elif filter_complex:
            cmd_final.extend(["-filter_complex", filter_complex[0], "-map", "0:v", "-map", "[aout]"])
        elif video_filters:
            cmd_final.extend(["-vf", ",".join(video_filters)] + audio_maps)
        else:
            cmd_final.extend(audio_maps)

        cmd_final.extend([
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "19",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(total_duration),
            str(final_p)
        ])

        try:
            subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            shutil.copy(str(merged_temp), str(final_p))

        if concat_list_file.exists():
            concat_list_file.unlink()
        if merged_temp.exists():
            merged_temp.unlink()

        return str(final_p)

    def _create_emoji_sticker(self, emoji_char: str, output_png_path: Path):
        """Video üzerine eklenecek devasa, yüksek kaliteli saydam emoji çıkartması çizer."""
        img = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # AppleColorEmoji veya standart font
        emoji_font = None
        for font_path in [
            "/System/Library/Fonts/Apple Color Emoji.ttc",
            "/System/Library/Fonts/Supplemental/AppleColorEmoji.ttc"
        ]:
            if os.path.exists(font_path):
                try:
                    emoji_font = ImageFont.truetype(font_path, 140)
                    break
                except Exception:
                    pass

        if not emoji_font:
            try:
                emoji_font = ImageFont.truetype(str(Path(FONTS_DIR) / "impact.ttf"), 120)
            except Exception:
                emoji_font = ImageFont.load_default()

        # Dairesel yarı saydam parlayan arka plan rozeti
        draw.ellipse([10, 10, 210, 210], fill=(255, 255, 255, 60), outline=(255, 255, 255, 180), width=4)
        draw.text((35, 25), emoji_char, font=emoji_font, embedded_color=True)
        img.save(str(output_png_path), format="PNG")

    def _get_audio_duration(self, audio_path: str) -> float:
        """Ses süresini saniye olarak ölçer."""
        try:
            cmd = [self.ffmpeg_exe, "-i", audio_path]
            result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            for line in result.stderr.split("\n"):
                if "Duration:" in line:
                    time_str = line.split("Duration:")[1].split(",")[0].strip()
                    h, m, s = time_str.split(":")
                    return float(h) * 3600 + float(m) * 60 + float(s)
        except Exception:
            pass
        return 3.0

    def _get_video_duration(self, video_path: str) -> float:
        return self._get_audio_duration(video_path)
