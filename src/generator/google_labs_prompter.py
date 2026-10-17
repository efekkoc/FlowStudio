import json
import random
import requests
from typing import Dict, Any, Optional

from config.settings import get_gemini_api_key
from src.generator.prompt_templates import GOOGLE_LABS_VEO_SYSTEM_PROMPT

VIRAL_RANDOM_SEEDS = [
    "adorable fluffy baby red panda baking sweet pastel strawberry cake in cozy kitchen",
    "tiny baby sea otter floating on back and playfully juggling glowing rainbow pearls",
    "chubby baby penguin wearing yellow knitted beanie sliding down crystal ice ramp",
    "sweet little cloud sprite bouncing across soft purple star clouds in twilight sky",
    "cute fluffy baby fox discovering sparkling crystal flowers inside glowing cave",
    "tiny baby elephant with big floppy ears spraying warm rainbow mist at butterfies",
    "adorable baby hedgehog wearing tiny acorn cap nibbling on giant juicy raspberry",
    "chubby baby raccoon gently washing glowing blue crystals in a fairytale spring",
    "tiny fluffy golden retriever puppy in red boots jumping into puddle of glowing flower petals",
    "sleepy baby owl sitting on velvet branch catching floating stardust bubbles",
    "cute chubby hamster running inside a giant glowing rainbow donut wheel",
    "tiny baby fawn with flower crown tiptoeing across magical glowing moss carpet"
]

FALLBACK_VEO_PROMPTS = [
    {
        "theme": "Baby Cloud Sprite",
        "master_video_prompt": "A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with a tiny, fluffy baby cloud sprite sitting on a glowing crescent moon in a pastel night sky. Next, it gently blows a soft puff of wind that turns into twinkling star-bubbles. Then, it happily bounces from cloud to cloud leaving a trail of shimmering stardust. Finally, camera zooms in as the little cloud sprite happily smiles and waves a tiny fluffy hand at audience. Bright pastel colors, smooth 60fps movement, magical soft lighting, low stimulation, cinematic 4K detail.",
        "title": "Sleepy Little Cloud Sprite's Starry Journey ✨🌙 #Shorts",
        "description": "Watch this adorable baby cloud sprite dance across the sleepy night sky! Perfect relaxing 3D animation for kids and bedtime vibes. #Shorts #LowStimulation #Pixar3D #Cute #Relaxing",
        "tags": ["Shorts", "3DAnimation", "Pixar", "LowStimulation", "Cute", "Relaxing", "BedtimeShorts"]
    },
    {
        "theme": "Baby Red Panda Bakery",
        "master_video_prompt": "A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with an adorable fluffy baby red panda in a tiny chef hat standing on a wooden stool in a cozy bakery. Next, the red panda happily kneads glowing pastel strawberry dough that puffs up into a heart shape. Then, it dusts rainbow powdered sugar into the air, giggling with delight. Finally, the red panda holds up a fresh warm pastry, smiling sweetly and winking at the audience. Warm golden ambient lighting, tactile textures, smooth 60fps cinematic 4K.",
        "title": "Baby Red Panda Makes Magical Strawberry Pastry! 🥐🍓 #Shorts",
        "description": "Sweetest little baby red panda baking fresh pastries in a warm cottage bakery. Satisfying, cozy and relaxing Pixar 3D animation. #Shorts #RedPanda #Baking #Cute #Pixar3D",
        "tags": ["Shorts", "3DAnimation", "Pixar", "RedPanda", "Cute", "Satisfying", "LowStimulation"]
    },
    {
        "theme": "Playful Baby Otter Pearls",
        "master_video_prompt": "A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with a tiny chubby baby otter floating peacefully on its back in a sparkling crystal-clear pond. Next, the otter playfully juggles three glowing pastel pearl bubbles on its tummy. Then, it dives underwater and does a joyful loop-the-loop, popping bubbles. Finally, the otter pops its head out of the water, resting its paws on its cheeks with an adorable happy grin directly at the camera. Soft sunbeams through water, gentle ripples, smooth 60fps 4K detail.",
        "title": "Baby Otter Playing With Magic Pearl Bubbles! 🦦🫧✨ #Shorts",
        "description": "Most adorable baby otter floating and playing with magical bubbles in a crystal pond. Soothing ASMR visual vibes. #Shorts #Otter #Cute #Pixar3D #LowStimulation",
        "tags": ["Shorts", "3DAnimation", "Pixar", "BabyOtter", "Cute", "Relaxing", "ASMR"]
    },
    {
        "theme": "Baby Penguin Ice Slide",
        "master_video_prompt": "A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with a tiny fluffy baby penguin wearing a cozy yellow pom-pom beanie standing atop a glittering pastel ice hill. Next, the penguin slides on its tummy down a smooth rainbow ice slide, giggling with joy. Then, it gently glides across a frozen mirror lake leaving glowing swirl trails. Finally, the little penguin slides right up to the camera, balancing on one foot, smiling brightly and waving both flippers warmly. Soft pastel aurora borealis glow, smooth 60fps cinematic 4K.",
        "title": "Tiny Penguin's Rainbow Ice Slide Adventure! 🐧❄️🌈 #Shorts",
        "description": "Joyful baby penguin in a yellow beanie sliding down rainbow ice! Uplifting and relaxing 3D animation. #Shorts #Penguin #Cute #Pixar3D #LowStimulation",
        "tags": ["Shorts", "3DAnimation", "Pixar", "Penguin", "Cute", "Winter", "Relaxing"]
    },
    {
        "theme": "Baby Fox Crystal Cave",
        "master_video_prompt": "A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with a fluffy baby red fox with big bright eyes stepping into a glowing cave filled with gentle pastel crystals. Next, the fox gently taps a pink crystal flower with its paw, causing it to chime musically and glow softly. Then, tiny friendly glowing fireflies surround the fox, illuminating its silky fur. Finally, the fox sits down, wraps its bushy white-tipped tail around its paws, and smiles warmly straight at the audience. Cozy magical glow, soothing ambiance, smooth 60fps 4K render.",
        "title": "Baby Fox Discovers Enchanted Musical Crystals! 🦊💎✨ #Shorts",
        "description": "Calming and magical scene of a baby fox exploring musical glowing crystal flowers. Pure ASMR visual comfort for kids. #Shorts #BabyFox #Cute #Pixar3D #Magical",
        "tags": ["Shorts", "3DAnimation", "Pixar", "BabyFox", "Cute", "Crystals", "LowStimulation"]
    },
    {
        "theme": "Baby Dragon Bubble Bath",
        "master_video_prompt": "A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with a tiny, chubby baby dragon taking a warm bubble bath in a wooden tub in a fairytale cottage. Next, the dragon sneezes a tiny spark that turns soapy water into colorful floating rainbow bubbles. Then, the dragon happily pops bubbles with its tiny paws. Finally, the baby dragon looks at the camera, wearing a bubble hat and giggling cheerfully. Soft pastel tones, cozy fireplace glow, smooth 60fps animation, low stimulation 4K render.",
        "title": "Baby Dragon Rainbow Bubble Bath! 🐉🛁✨ #Shorts",
        "description": "Sweet little baby dragon enjoying a warm bubble bath and popping rainbow bubbles. Calming 3D Pixar style short. #Shorts #BabyDragon #Cute #Pixar3D #LowStimulation",
        "tags": ["Shorts", "3DAnimation", "Pixar", "LowStimulation", "Cute", "BabyDragon", "Relaxing", "KidsAnimation"]
    },
    {
        "theme": "Mini Bear Pancake Tower",
        "master_video_prompt": "A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with an adorable fluffy baby teddy bear standing on a wooden stool in a sunny kitchen, stacking golden fluffy pancakes. Next, the bear gently pours glowing golden honey and fresh blueberries on top. Then, a tiny honey drip bounces in slow motion. Finally, the baby bear licks honey off its paw, smiling with pure joy directly into the camera. Cozy warm lighting, velvety textures, satisfying physics, 60fps cinematic 4K.",
        "title": "Tiny Bear Makes The Ultimate Honey Pancake Tower! 🥞🍯✨ #Shorts",
        "description": "Satisfying and cozy 3D animated scene of a little teddy bear building a pancake tower with honey. #Shorts #Pancakes #TeddyBear #Satisfying #Pixar3D",
        "tags": ["Shorts", "3DAnimation", "Pixar", "Satisfying", "TeddyBear", "Pancakes", "LowStimulation"]
    },
    {
        "theme": "Low-Stimulation Baby Bunny",
        "master_video_prompt": "A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with a cute, fluffy baby bunny waking up in a cozy hollow tree house in a colorful pastel forest. Next, the bunny puts on tiny shiny red boots and playfully jumps over a giant glowing mushroom in a sunny clearing. Then, the bunny floats gently on a soft star-shaped cloud, giggling. Finally, the camera zooms in on the bunny smiling happily and waving warmly at the audience. Bright pastel colors, smooth 60fps movement, magical lighting, low stimulation, cinematic 4K detail.",
        "title": "Cute 3D Pixar Baby Bunny Magical Morning! 🐰✨ #Shorts",
        "description": "Adorable 3D animation of a baby bunny waking up and exploring a magical glowing forest. Low stimulation and calming for toddlers. #Shorts #Cute #Pixar3D #LowStimulation #BabyBunny",
        "tags": ["Shorts", "3DAnimation", "Pixar", "LowStimulation", "Cute", "BabyBunny", "ToddlerShorts", "ASMR"]
    }
]


class GoogleLabsPrompter:
    def __init__(self):
        self.api_key = get_gemini_api_key()

    def generate_master_prompt(self, custom_topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Google Flow (Veo 3.1) için 10 saniyelik kesintisiz, tamamen özgün, viral 3D Pixar promptu ve YouTube SEO metinleri üretir.
        Her çağrıda farklı bir viral tohum kullanır.
        """
        # Rastgele viral tohum seç
        chosen_seed = random.choice(VIRAL_RANDOM_SEEDS)
        user_prompt_instruction = f"Generate a completely fresh, unique, viral, 10-second 3D Pixar animated vertical video prompt for YouTube Shorts."
        
        if custom_topic and len(custom_topic.strip()) > 0:
            user_prompt_instruction += f" Theme/Character: {custom_topic}."
        else:
            user_prompt_instruction += f" Fresh Inspiration Seed: {chosen_seed}. Make it totally unique with delightful details."

        if self.api_key and len(self.api_key.strip()) > 5:
            # Gemini REST API ile doğrudan çağrı (gemini-flash-lite-latest ve fallback modelleri)
            models_to_try = ["gemini-flash-lite-latest", "gemini-3.6-flash"]
            for model_name in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": user_prompt_instruction}]}],
                        "systemInstruction": {"parts": [{"text": GOOGLE_LABS_VEO_SYSTEM_PROMPT}]},
                        "generationConfig": {"responseMimeType": "application/json"}
                    }
                    r = requests.post(url, json=payload, timeout=20)
                    if r.status_code == 200:
                        data = json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
                        # 10 saniye kuralını sağla
                        if "25-second" in data.get("master_video_prompt", ""):
                            data["master_video_prompt"] = data["master_video_prompt"].replace("25-second", "10-second")
                        print(f"[GoogleLabsPrompter] Gemini ({model_name}) ile yeni viral prompt üretildi: {data.get('title')}")
                        return data
                except Exception as e:
                    print(f"[GoogleLabsPrompter] Model {model_name} denemesi başarısız: {e}")

        print("[GoogleLabsPrompter] Zengin yedek şablon havuzundan rastgele seçiliyor...")
        return self._get_fallback_prompt(custom_topic)

    def _get_fallback_prompt(self, custom_topic: Optional[str] = None) -> Dict[str, Any]:
        if custom_topic:
            # Konu eşleşmesi varsa bul
            for item in FALLBACK_VEO_PROMPTS:
                if any(w.lower() in item["theme"].lower() for w in custom_topic.split()):
                    return item.copy()

        # Rastgele farklı bir şablon seç
        chosen = random.choice(FALLBACK_VEO_PROMPTS).copy()
        if custom_topic:
            chosen["theme"] = custom_topic[:30]
            chosen["title"] = f"Adorable 3D Pixar {custom_topic[:25]} Magic! ✨ #Shorts"
            chosen["description"] = f"Cozy and relaxing 3D animation featuring {custom_topic}. Low stimulation aesthetic. #Shorts #Cute #Pixar3D #Relaxing"
            chosen["master_video_prompt"] = f"A continuous 10-second 3D Pixar animated vertical video (9:16 aspect ratio) for young kids. Starts with {custom_topic} in a magical cozy setting. Next, playful gentle interaction. Then, sparkling floating bubbles or soft magic. Finally, smiling happily and waving warmly at audience. Bright pastel colors, smooth 60fps movement, magical lighting, low stimulation, cinematic 4K detail."
        return chosen
