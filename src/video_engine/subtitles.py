import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
from config.settings import FONTS_DIR


class SubtitleEngine:
    def __init__(self, font_path: str = None):
        self.font_path = font_path or str(Path(FONTS_DIR) / "impact.ttf")
        if not os.path.exists(self.font_path):
            self.font_path = str(Path(FONTS_DIR) / "arial_black.ttf")

    def create_ass_subtitles(
        self,
        word_timings: List[Dict[str, Any]],
        output_ass_path: str,
        highlight_color: str = "&H0000FFFF",  # ASS format: BGR (Sarı: &H0000FFFF)
        primary_color: str = "&H00FFFFFF",    # Beyaz
        outline_color: str = "&H00000000",    # Siyah
        font_size: int = 56
    ) -> str:
        """
        FFmpeg ile doğrudan videoya gömülebilen animasyonlu ASS altyazı dosyası üretir.
        Kelime kelime renk vurgusu (karaoke efekti) uygular.
        """
        output_path = Path(output_ass_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsStyle,Impact,{font_size},{primary_color},{highlight_color},{outline_color},&H80000000,1,0,0,0,100,100,2,0,1,8,4,2,40,40,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        # Kelimeleri 2-4'lü gruplara (chunks) bölerek ekranda okunaklı tutalım
        chunks = self._group_words(word_timings, max_words=3)
        events = []

        for chunk in chunks:
            if not chunk:
                continue
            chunk_start = self._format_ass_time(chunk[0]["start"])
            chunk_end = self._format_ass_time(chunk[-1]["end"] + 0.1)

            # Her kelime için karaoke/vurgu zamanı hesapla
            text_parts = []
            for w in chunk:
                dur_cs = int((w["end"] - w["start"]) * 100)
                word_clean = w["word"].upper()
                text_parts.append(f"{{\\k{dur_cs}}}{word_clean}")

            dialogue_text = " ".join(text_parts)
            events.append(f"Dialogue: 0,{chunk_start},{chunk_end},ShortsStyle,,0,0,0,,{dialogue_text}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ass_header + "\n".join(events))

        return str(output_path)

    def _group_words(self, word_timings: List[Dict[str, Any]], max_words: int = 3) -> List[List[Dict[str, Any]]]:
        """Kelimeleri ekranda 2-3 kelimelik hızlı bloklar halinde gruplar."""
        grouped = []
        current_group = []
        
        for w in word_timings:
            current_group.append(w)
            # Noktalama işareti veya maksimum kelimeye ulaşıldığında yeni satıra geç
            if len(current_group) >= max_words or any(punct in w["word"] for punct in [".", "!", "?", ","]):
                grouped.append(current_group)
                current_group = []
        
        if current_group:
            grouped.append(current_group)
            
        return grouped

    def _format_ass_time(self, seconds: float) -> str:
        """Saniyeyi ASS zaman formatına (H:MM:SS.CS) çevirir."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds - int(seconds)) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

    def render_subtitle_overlay_image(
        self,
        text: str,
        highlight_idx: int = -1,
        width: int = 1080,
        height: int = 1920,
        font_size: int = 68
    ) -> Image.Image:
        """PIL kullanarak yüksek çözünürlüklü saydam altyazı katmanı oluşturur."""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except Exception:
            font = ImageFont.load_default()

        words = text.upper().split()
        if not words:
            return img

        # Kelimelerin toplam genişliğini hesapla
        word_widths = []
        space_width = draw.textlength(" ", font=font)
        for w in words:
            word_widths.append(draw.textlength(w, font=font))

        total_width = sum(word_widths) + (len(words) - 1) * space_width
        start_x = (width - total_width) / 2
        y_pos = height - 520

        current_x = start_x
        for i, word in enumerate(words):
            fill_color = (255, 230, 0, 255) if i == highlight_idx else (255, 255, 255, 255)
            stroke_color = (0, 0, 0, 255)

            draw.text(
                (current_x, y_pos),
                word,
                font=font,
                fill=fill_color,
                stroke_width=8,
                stroke_fill=stroke_color
            )
            current_x += word_widths[i] + space_width

        return img
