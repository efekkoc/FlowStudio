import os
import math
import struct
import wave
import random
from pathlib import Path
from typing import Optional
from config.settings import MUSIC_DIR, SFX_DIR


class AudioManager:
    def __init__(self):
        self.music_dir = Path(MUSIC_DIR)
        self.sfx_dir = Path(SFX_DIR)
        self._ensure_default_sfx()

    def _ensure_default_sfx(self):
        """Temel çizgi film ses efektlerini (boing, pop, whoosh, sparkle, laugh) otomatik üretir."""
        self._generate_boing_sfx(self.sfx_dir / "boing.wav")
        self._generate_pop_sfx(self.sfx_dir / "pop.wav")
        self._generate_whoosh_sfx(self.sfx_dir / "whoosh.wav")
        self._generate_sparkle_sfx(self.sfx_dir / "sparkle.wav")
        self._generate_cheer_sfx(self.sfx_dir / "cheer.wav")
        self._generate_bg_music(self.music_dir / "playful_kids_loop.wav")

    def get_sfx(self, sfx_name: str) -> Optional[str]:
        """İstenen ses efektinin dosya yolunu döner."""
        clean_name = sfx_name.lower().replace(".wav", "").replace(".mp3", "")
        file_path = self.sfx_dir / f"{clean_name}.wav"
        if file_path.exists():
            return str(file_path)
        
        # mp3 kontrolü
        mp3_path = self.sfx_dir / f"{clean_name}.mp3"
        if mp3_path.exists():
            return str(mp3_path)

        # Varsayılan pop sesi
        default_pop = self.sfx_dir / "pop.wav"
        return str(default_pop) if default_pop.exists() else None

    def get_background_music(self) -> Optional[str]:
        """Klasördeki telifsiz fon müziklerinden rastgele birini seçer."""
        music_files = list(self.music_dir.glob("*.mp3")) + list(self.music_dir.glob("*.wav"))
        if music_files:
            return str(random.choice(music_files))
        return None

    def _generate_boing_sfx(self, output_path: Path):
        """Çizgi film zıplama (boing) sesi üretir."""
        if output_path.exists():
            return
        sample_rate = 44100
        duration = 0.5
        n_samples = int(sample_rate * duration)
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            for i in range(n_samples):
                t = i / sample_rate
                # Pitch sweeps up and oscillates
                freq = 200 + 400 * t + 60 * math.sin(2 * math.pi * 18 * t)
                env = math.exp(-4 * t)
                val = int(32767 * 0.7 * env * math.sin(2 * math.pi * freq * t))
                wav_file.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    def _generate_pop_sfx(self, output_path: Path):
        """Kısa patlama / baloncuk (pop) sesi üretir."""
        if output_path.exists():
            return
        sample_rate = 44100
        duration = 0.15
        n_samples = int(sample_rate * duration)
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            for i in range(n_samples):
                t = i / sample_rate
                freq = 800 - 500 * (t / duration)
                env = math.exp(-20 * t)
                val = int(32767 * 0.8 * env * math.sin(2 * math.pi * freq * t))
                wav_file.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    def _generate_whoosh_sfx(self, output_path: Path):
        """Rüzgar / hızlı geçiş (whoosh) sesi üretir."""
        if output_path.exists():
            return
        sample_rate = 44100
        duration = 0.4
        n_samples = int(sample_rate * duration)
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            for i in range(n_samples):
                t = i / sample_rate
                # White noise filtered
                noise = (random.random() * 2 - 1)
                env = math.sin(math.pi * (t / duration)) ** 2
                val = int(32767 * 0.6 * env * noise)
                wav_file.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    def _generate_sparkle_sfx(self, output_path: Path):
        """Sihirli parıltı (sparkle) sesi üretir."""
        if output_path.exists():
            return
        sample_rate = 44100
        duration = 0.6
        n_samples = int(sample_rate * duration)
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            for i in range(n_samples):
                t = i / sample_rate
                freq = 1200 + 600 * math.sin(2 * math.pi * 12 * t)
                env = math.exp(-3 * t)
                val = int(32767 * 0.5 * env * math.sin(2 * math.pi * freq * t))
                wav_file.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    def _generate_cheer_sfx(self, output_path: Path):
        """Sevinç / alkış tınısı üretir."""
        if output_path.exists():
            return
        sample_rate = 44100
        duration = 0.8
        n_samples = int(sample_rate * duration)
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            for i in range(n_samples):
                t = i / sample_rate
                val_chords = (
                    math.sin(2 * math.pi * 523.25 * t) +
                    math.sin(2 * math.pi * 659.25 * t) +
                    math.sin(2 * math.pi * 783.99 * t)
                ) / 3.0
                env = math.exp(-2.5 * t)
                val = int(32767 * 0.6 * env * val_chords)
                wav_file.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    def _generate_bg_music(self, output_path: Path):
        """Neşeli, hafif çocuk fon müziği döngüsü üretir."""
        if output_path.exists():
            return
        sample_rate = 44100
        duration = 16.0  # 16 saniyelik loop
        n_samples = int(sample_rate * duration)
        notes = [261.63, 329.63, 392.00, 523.25, 440.00, 349.23, 392.00, 329.63]  # C E G C A F G E
        note_len = 0.5  # her nota 0.5s

        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            for i in range(n_samples):
                t = i / sample_rate
                note_idx = int((t / note_len) % len(notes))
                freq = notes[note_idx]
                t_note = t % note_len
                env = math.exp(-3 * t_note)
                # Marimba/Xylophone synth sound
                sample = (math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)) * env
                val = int(32767 * 0.25 * sample)
                wav_file.writeframes(struct.pack('<h', max(-32768, min(32767, val))))
