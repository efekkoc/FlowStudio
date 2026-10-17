import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import edge_tts
from config.settings import VOICE_PREVIEWS_DIR, VOICE_PRESETS


class TTSEngine:
    def __init__(self, default_voice: str = "en-US-AnaNeural"):
        self.default_voice = default_voice
        self.preview_dir = Path(VOICE_PREVIEWS_DIR)
        self.preview_dir.mkdir(parents=True, exist_ok=True)

    async def generate_speech_async(
        self,
        text: str,
        output_audio_path: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> Dict[str, Any]:
        """
        Edge-TTS kullanarak ses ve kelime zaman damgaları üretir.
        """
        selected_voice = voice or self.default_voice
        communicate = edge_tts.Communicate(text, selected_voice, rate=rate, pitch=pitch)
        
        audio_data = bytearray()
        sentence_boundaries = []
        word_boundaries = []

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                offset = chunk["offset"] / 10_000_000.0
                duration = chunk["duration"] / 10_000_000.0
                sentence_boundaries.append({
                    "text": chunk["text"],
                    "offset": offset,
                    "duration": duration
                })
            elif chunk["type"] == "WordBoundary":
                offset = chunk["offset"] / 10_000_000.0
                duration = chunk["duration"] / 10_000_000.0
                word_boundaries.append({
                    "word": chunk["text"],
                    "start": offset,
                    "end": offset + duration
                })

        output_path = Path(output_audio_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_data)

        final_word_timings: List[Dict[str, Any]] = []
        total_duration = 0.0

        if word_boundaries:
            final_word_timings = word_boundaries
            total_duration = word_boundaries[-1]["end"]
        elif sentence_boundaries:
            for sb in sentence_boundaries:
                s_text = sb["text"]
                s_start = sb["offset"]
                s_dur = sb["duration"]
                words = s_text.split()
                if not words:
                    continue
                total_chars = sum(len(w) for w in words)
                w_curr_start = s_start
                for w in words:
                    w_dur = s_dur * (len(w) / max(1, total_chars))
                    final_word_timings.append({
                        "word": w,
                        "start": w_curr_start,
                        "end": w_curr_start + w_dur
                    })
                    w_curr_start += w_dur
                total_duration = max(total_duration, sb["offset"] + sb["duration"])
        else:
            words = text.split()
            w_start = 0.0
            w_dur = 0.4
            for w in words:
                final_word_timings.append({
                    "word": w,
                    "start": w_start,
                    "end": w_start + w_dur
                })
                w_start += w_dur
            total_duration = w_start

        return {
            "audio_path": str(output_path),
            "word_timings": final_word_timings,
            "duration": total_duration,
            "text": text,
            "voice": selected_voice
        }

    def generate_speech(
        self,
        text: str,
        output_audio_path: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> Dict[str, Any]:
        """Senkron wrapper metod."""
        return asyncio.run(
            self.generate_speech_async(
                text=text,
                output_audio_path=output_audio_path,
                voice=voice,
                rate=rate,
                pitch=pitch
            )
        )

    def get_voice_preview_path(self, voice_key: str) -> Optional[str]:
        """Panelde anında dinlenebilmesi için ses önizleme dosyası döner veya üretir."""
        if voice_key not in VOICE_PRESETS:
            return None
        v_info = VOICE_PRESETS[voice_key]
        voice_id = v_info["id"]
        preview_file = self.preview_dir / f"{voice_id}.mp3"
        
        if not preview_file.exists() or preview_file.stat().st_size < 1000:
            sample_text = v_info.get("preview_text", "Hello, this is a sample preview voice.")
            try:
                self.generate_speech(text=sample_text, output_audio_path=str(preview_file), voice=voice_id)
            except Exception as e:
                print(f"[TTS] Önizleme ses dosyası oluşturulamadı: {e}")
                return None
        return str(preview_file)
