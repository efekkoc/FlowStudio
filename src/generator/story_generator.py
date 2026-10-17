import json
import random
import re
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from config.settings import get_gemini_api_key, STYLE_PRESETS
from src.generator.prompt_templates import KIDS_ANIMATION_SYSTEM_PROMPT, VIRAL_THEMES


class Scene(BaseModel):
    scene_id: int
    narration: str
    image_prompt: str
    sfx_keyword: Optional[str] = "pop"
    camera_motion: Optional[str] = "rapid_zoom_in"
    emoji_overlay: Optional[str] = "✨"


class VideoStory(BaseModel):
    title: str
    description: str
    tags: List[str] = Field(default_factory=list)
    theme: str
    character_description: Optional[str] = ""
    scenes: List[Scene]


class StoryGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def _get_active_api_key(self) -> str:
        return self.api_key or get_gemini_api_key() or os.getenv("GEMINI_API_KEY", "")

    def generate_story(
        self,
        topic: Optional[str] = None,
        style_key: str = "pixar_3d",
        num_scenes: int = 5
    ) -> VideoStory:
        """
        Gemini 3.6 Flash ile 20 saniyelik sinematik sahne-sahne döküm (scene-by-scene breakdown) üretir.
        """
        chosen_topic = topic if (topic and len(topic.strip()) > 3) else random.choice(VIRAL_THEMES)
        style_info = STYLE_PRESETS.get(style_key, STYLE_PRESETS["pixar_3d"])
        style_desc = style_info["description"] if isinstance(style_info, dict) else str(style_info)

        user_prompt = f"""
Give me a scene-by-scene cinematic breakdown for a 20-second viral YouTube Shorts animation video about: "{chosen_topic}".
Target: Exactly {num_scenes} continuous fast-paced action scenes (approx. 20-25 seconds total).
Visual Style: "{style_desc}".

DIRECTOR REQUIREMENTS:
1. Scene 1 MUST be an explosive visual hook.
2. Maintain STRICT character continuity across all scenes.
3. Spoken American English dialogue must be snappy, funny, and high energy.

Return ONLY a valid JSON object matching the schema.
"""

        active_key = self._get_active_api_key()

        if active_key and len(active_key.strip()) > 5:
            try:
                story_data = self._call_gemini(user_prompt, active_key)
                return VideoStory(**story_data)
            except Exception as e:
                print(f"[StoryGenerator] Gemini API hatası: {e}. Zengin dinamik havuz kullanılıyor.")

        return self._generate_diverse_fallback_story(chosen_topic, style_desc, num_scenes)

    def _call_gemini(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """Google Gemini API (gemini-3.6-flash) çağrısı."""
        from google import genai
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "system_instruction": KIDS_ANIMATION_SYSTEM_PROMPT,
                "response_mime_type": "application/json",
            }
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n", "", text)
            text = re.sub(r"\n```$", "", text)
            
        return json.loads(text)

    def _generate_diverse_fallback_story(self, topic: str, style_desc: str, num_scenes: int) -> VideoStory:
        """API çevrimdışıyken farklı ve özgün senaryolar üreten havuz."""
        stories_pool = [
            {
                "title": "Chubby Kitten Stolen Pancake Tower! 🥞🐱 #Shorts",
                "description": "Watch what happens when this greedy kitty jumps on a 100-foot pancake! 😂 #Shorts #Animation #Cartoon #Funny #Pixar",
                "tags": ["shorts", "funnycat", "cartoon", "pixarstyle", "animation", "viralshorts"],
                "theme": "Funny Cat Pancake Adventure",
                "character_description": "Chubby ginger tabby kitten with giant sparkly emerald eyes wearing a tiny red chef hat",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "This greedy little kitty just found the biggest pancake tower in the world!",
                        "image_prompt": f"Close-up action shot of a chubby ginger tabby kitten with big sparkling green eyes in a tiny red chef hat looking in shock at a giant 100-foot pancake tower dripping with syrup, {style_desc}",
                        "sfx_keyword": "pop",
                        "camera_motion": "rapid_zoom_in",
                        "emoji_overlay": "🥞"
                    },
                    {
                        "scene_id": 2,
                        "narration": "He jumps straight onto the melted butter trampoline! BOING!",
                        "image_prompt": f"Action shot of the chubby ginger kitten in red chef hat bouncing high off a yellow melting butter cube on pancakes, paws in the air, funny thrilled face, flying syrup, {style_desc}",
                        "sfx_keyword": "boing",
                        "camera_motion": "punch_zoom",
                        "emoji_overlay": "💥"
                    },
                    {
                        "scene_id": 3,
                        "narration": "Whoosh! The whole tower starts tumbling down!",
                        "image_prompt": f"Wide dynamic shot of the huge pancake tower falling sideways like dominoes, the chubby ginger kitten surfing on the top pancake, funny panicked expression, {style_desc}",
                        "sfx_keyword": "whoosh",
                        "camera_motion": "screen_shake",
                        "emoji_overlay": "😱"
                    },
                    {
                        "scene_id": 4,
                        "narration": "SPLASH! He lands right in a giant bowl of whipped cream!",
                        "image_prompt": f"Hilarious splash shot of the chubby ginger kitten covered in fluffy white whipped cream with only big green eyes visible, cherry on head, {style_desc}",
                        "sfx_keyword": "sparkle",
                        "camera_motion": "punch_zoom",
                        "emoji_overlay": "🍒"
                    },
                    {
                        "scene_id": 5,
                        "narration": "And now he wants to eat his way out for dinner!",
                        "image_prompt": f"Super cute ending of the chubby ginger kitten happily licking whipped cream with round tummy, grinning with sparkles, {style_desc}",
                        "sfx_keyword": "laugh",
                        "camera_motion": "pop_zoom",
                        "emoji_overlay": "😋"
                    }
                ]
            },
            {
                "title": "Baby Penguin Hijacks Ice Rollercoaster! 🐧🕶️ #Shorts",
                "description": "Never give sunglasses to a baby penguin! 😂 #Shorts #KidsAnimation #Penguin #Funny #Pixar",
                "tags": ["shorts", "babypenguin", "rollercoaster", "cartoon", "animation", "viral"],
                "theme": "Penguin Rollercoaster",
                "character_description": "Cute chubby baby penguin wearing cool black sunglasses and a red scarf",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "Wait... did that baby penguin just sneak onto the giant ice rollercoaster?!",
                        "image_prompt": f"Close-up of a cute chubby baby penguin wearing black sunglasses and a red scarf standing on top of an icy rollercoaster track, grinning mischievously, {style_desc}",
                        "sfx_keyword": "pop",
                        "camera_motion": "rapid_zoom_in",
                        "emoji_overlay": "🐧"
                    },
                    {
                        "scene_id": 2,
                        "narration": "He jumps in the front cart and hits the turbo button! WHOOSH!",
                        "image_prompt": f"Action shot of the baby penguin in sunglasses zooming at lightning speed down a vertical ice track, scarf flying back, funny excited expression, {style_desc}",
                        "sfx_keyword": "whoosh",
                        "camera_motion": "punch_zoom",
                        "emoji_overlay": "⚡"
                    },
                    {
                        "scene_id": 3,
                        "narration": "He loops upside down through a giant frozen donut!",
                        "image_prompt": f"Dynamic shot of the rollercoaster cart doing a 360 loop-de-loop through a giant glittering ice ring, sparkling snowflakes flying, {style_desc}",
                        "sfx_keyword": "sparkle",
                        "camera_motion": "screen_shake",
                        "emoji_overlay": "🍩"
                    },
                    {
                        "scene_id": 4,
                        "narration": "And lands safely in a giant snow cone! Best ride ever!",
                        "image_prompt": f"Funny ending shot of the baby penguin happily sliding down a giant rainbow snow cone holding a tiny spoon, smiling with sparkles, {style_desc}",
                        "sfx_keyword": "cheer",
                        "camera_motion": "pop_zoom",
                        "emoji_overlay": "🍧"
                    }
                ]
            }
        ]

        chosen = random.choice(stories_pool)
        return VideoStory(**chosen)
