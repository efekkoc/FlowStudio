import os
from pathlib import Path
from dotenv import load_dotenv

# Ana Proje Dizini
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv(override=True)

# API Anahtarları
def get_gemini_api_key():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    return os.getenv("GEMINI_API_KEY", "")

GEMINI_API_KEY = get_gemini_api_key()
YOUTUBE_CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", str(BASE_DIR / "client_secrets.json"))

# Klasör Yolları
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
SFX_DIR = ASSETS_DIR / "sfx"
FONTS_DIR = ASSETS_DIR / "fonts"
VOICE_PREVIEWS_DIR = ASSETS_DIR / "voice_previews"

OUTPUT_DIR = BASE_DIR / "output"
CANDIDATES_DIR = OUTPUT_DIR / "candidates"
APPROVED_DIR = OUTPUT_DIR / "approved"

for path in [ASSETS_DIR, MUSIC_DIR, SFX_DIR, FONTS_DIR, VOICE_PREVIEWS_DIR, CANDIDATES_DIR, APPROVED_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Video Format Ayarları (1080x1920 9:16 Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Genişletilmiş US Amerikan İngilizcesi Ses Seçenekleri
VOICE_PRESETS = {
    "us_kid_ana": {
        "id": "en-US-AnaNeural",
        "name": "👧 Ana (Cute Child Voice - US)",
        "preview_text": "Hi friends! Look at what I just found, it is so amazing!",
        "gender": "Female"
    },
    "us_boy_andrew": {
        "id": "en-US-AndrewNeural",
        "name": "👦 Andrew (Energetic Boy - US)",
        "preview_text": "Whoa! Hold on tight, we are about to go super fast!",
        "gender": "Male"
    },
    "us_friendly_christopher": {
        "id": "en-US-ChristopherNeural",
        "name": "🎙️ Christopher (Friendly Storyteller - US)",
        "preview_text": "Once upon a time in a magical candy forest, something wild happened!",
        "gender": "Male"
    },
    "us_aria_cheerful": {
        "id": "en-US-AriaNeural",
        "name": "✨ Aria (Expressive & Cheerful - US)",
        "preview_text": "You are NOT going to believe what happened next!",
        "gender": "Female"
    },
    "us_guy_comedy": {
        "id": "en-US-GuyNeural",
        "name": "🤪 Guy (Funny / Cartoon Comedy - US)",
        "preview_text": "Wait wait wait... did he really just try to eat that whole cake?!",
        "gender": "Male"
    },
    "us_jenny_sweet": {
        "id": "en-US-JennyNeural",
        "name": "🎀 Jenny (Sweet & Playful - US)",
        "preview_text": "Look at those sparkly rainbow bubbles dancing in the sky!",
        "gender": "Female"
    }
}

# 3D Animasyon Odaklı Görsel Stiller (Ultra 3D CGI & Pixar / Unreal Engine 5 Kalitesi)
STYLE_PRESETS = {
    "pixar_3d": {
        "title": "🧸 3D Pixar / Disney Movie (Ana Stil - Önerilen)",
        "description": "3D Disney Pixar animated feature film style, 3D CGI character render, octane render, Unreal Engine 5 cinematic lighting, subsurface scattering on 3D skin and fur, 3D depth of field, 8k volumetric shadows, vibrant colors, 9:16 vertical framing, strictly 3D animation"
    },
    "fluffy_3d_monster": {
        "title": "👾 3D Pofuduk Sevimli Canavarlar (3D Fur Physics)",
        "description": "Ultra detailed 3D CGI fluffy monster, simulated soft pastel fur physics, huge glossy reflective 3D eyes, volumetric glowing lighting, Pixar quality 3D character render, 9:16 vertical"
    },
    "candy_3d_wonderland": {
        "title": "🍫 3D Çikolata & Şeker Dünyası (3D Sweet Fantasy)",
        "description": "Magical 3D world where everything is sculpted from glossy 3D chocolate, glowing translucent gummy bears, liquid strawberry syrup splashes, 3D Pixar CGI movie render, 9:16 vertical"
    },
    "dreamworks_3d_animals": {
        "title": "🐾 3D Sevimli Hayvanlar (DreamWorks / Illumination 3D)",
        "description": "Super cute 3D stylized baby animal character, DreamWorks animation movie aesthetic, expressive 3D face, soft 3D fur shader, sunny volumetric lighting, 9:16 vertical"
    },
    "voxel_3d_minecraft": {
        "title": "🕹️ 3D Voxel / Minecraft 3D Blok Animasyonu",
        "description": "Vibrant 3D voxel cubic block animation style, cute Minecraft movie aesthetic, ray-traced 3D blocky lighting, 9:16 vertical"
    },
    "cyber_3d_robot": {
        "title": "🤖 3D Fütüristik Robot & Uzay Maceraları",
        "description": "Adorable 3D sci-fi robot animation, metallic glossy materials, glowing neon LED eyes, holographic 3D particle sparkles, Wall-E meets Pixar 3D aesthetic, 9:16 vertical"
    }
}
