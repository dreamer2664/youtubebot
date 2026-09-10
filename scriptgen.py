"""Script generation: turns a channel topic into a narrated scene list.

Two providers:
  * GeminiProvider  - Google AI Studio, free tier, needs a free API key.
  * TemplateProvider - no key, no network, always works, lower quality.

Both return the same Script object, so the rest of the pipeline does not care.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from typing import Protocol

import requests

from config import Config


@dataclass
class Scene:
    narration: str
    image_prompt: str


@dataclass
class Script:
    title: str
    description: str
    tags: list[str]
    scenes: list[Scene]
    provider: str = "unknown"

    def estimated_seconds(self, words_per_minute: float = 155.0) -> float:
        words = sum(len(s.narration.split()) for s in self.scenes)
        return round(words / words_per_minute * 60.0, 1)


class ScriptProvider(Protocol):
    name: str

    def generate(self, cfg: Config, topic_override: str | None = None) -> Script: ...


# --------------------------------------------------------------------------
# JSON extraction — LLMs wrap JSON in fences or add prose. Be forgiving.
# --------------------------------------------------------------------------
def extract_json(text: str) -> dict:
    text = text.strip()

    # strip markdown fences
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # fall back to the outermost balanced braces
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in model output: {text[:200]!r}")
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : index + 1])
    raise ValueError("Unbalanced JSON in model output")


def normalise_script(raw: dict, provider: str) -> Script:
    scenes = []
    for item in raw.get("scenes") or []:
        narration = str(item.get("narration") or item.get("text") or "").strip()
        prompt = str(item.get("image_prompt") or item.get("image") or "").strip()
        if not narration:
            continue
        if not prompt:
            prompt = narration[:180]
        scenes.append(Scene(narration=narration, image_prompt=prompt))

    if not scenes:
        raise ValueError("Model returned no usable scenes")

    title = str(raw.get("title") or "Untitled").strip()[:100]
    description = str(raw.get("description") or "").strip()
    tags = [str(t).strip() for t in (raw.get("tags") or []) if str(t).strip()]
    return Script(title=title, description=description, tags=tags, scenes=scenes, provider=provider)


# --------------------------------------------------------------------------
# Gemini
# --------------------------------------------------------------------------
class GeminiProvider:
    name = "gemini"

    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        if not api_key:
            raise RuntimeError(
                "No Gemini API key. Get a free one at https://aistudio.google.com/apikey, "
                "then put it in config.yaml or export GEMINI_API_KEY. "
                "Or set ai.provider: template in config.yaml to run keyless."
            )
        self.api_key = api_key
        self.model = model

    def generate(self, cfg: Config, topic_override: str | None = None) -> Script:
        topic = topic_override or cfg.topic
        target = cfg.target_seconds
        # roughly 155 words/minute of narration
        scene_count = max(3, min(10, round(target / 22)))

        prompt = f"""You are a script writer for a YouTube channel.

CHANNEL TOPIC: {topic}
TONE: {cfg.tone}
AUDIENCE: {cfg.audience}
LANGUAGE: {cfg.language}
TARGET VIDEO LENGTH: about {target} seconds

Pick ONE specific, genuinely interesting story or fact within the topic.
Write {scene_count} scenes of narration that together take about {target} seconds
when read aloud (roughly {int(target * 2.6)} words total).

Requirements:
- narration: plain spoken prose for a voiceover. No stage directions, no quotes
  inside the text, no markdown, no emoji.
- image_prompt: a detailed visual description for an AI image generator matching
  that scene. Photorealistic, cinematic, specific. No text or watermarks in image.
- Be factually careful. If a detail is uncertain, leave it out rather than invent it.

Return ONLY a JSON object in exactly this shape:
{{
  "title": "engaging video title, under 70 characters",
  "description": "2-4 sentence video description",
  "tags": ["up to 12 relevant tags"],
  "scenes": [
    {{"narration": "...", "image_prompt": "..."}}
  ]
}}"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.9,
                "responseMimeType": "application/json",
            },
        }
        response = requests.post(
            self.URL.format(model=self.model),
            params={"key": self.api_key},
            json=payload,
            timeout=180,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Gemini request failed (HTTP {response.status_code}): {response.text[:400]}"
            )

        data = response.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected Gemini response shape: {str(data)[:400]}") from exc

        script = normalise_script(extract_json(text), self.name)
        if not script.description:
            script.description = f"{script.title}\n\n{topic}"
        return script


# --------------------------------------------------------------------------
# Template fallback — no key, no network.
# --------------------------------------------------------------------------
class TemplateProvider:
    name = "template"

    FRAMINGS = [
        "The untold story of",
        "What really happened during",
        "The strange truth about",
        "Nobody talks about",
        "A forgotten chapter of",
    ]

    def generate(self, cfg: Config, topic_override: str | None = None) -> Script:
        topic = topic_override or cfg.topic
        seed = random.choice(self.FRAMINGS)
        title = f"{seed} {topic}"[:100]

        beats = [
            f"Today we look at {topic}, a subject that is far stranger than most people realise.",
            f"To understand it, we have to start with the context, because {topic} did not "
            f"happen in isolation.",
            "The details that survive are specific, and they are the reason this story still "
            "holds up today.",
            "There is a moment in this account that changes how you read everything before it.",
            f"So what does {topic} actually tell us? More than you would expect.",
        ]

        scenes = [
            Scene(narration=beat, image_prompt=f"cinematic photorealistic scene depicting {topic}")
            for beat in beats
        ]

        return Script(
            title=title,
            description=(
                f"{title}\n\nA short documentary-style look at {topic}.\n\n"
                "Generated with the offline template provider — add a free Gemini key "
                "to config.yaml for much better scripts."
            ),
            tags=[w for w in re.findall(r"[A-Za-z]{4,}", topic)][:12],
            scenes=scenes,
            provider=self.name,
        )


def get_provider(cfg: Config) -> ScriptProvider:
    """Return the configured provider, falling back to templates if unusable."""
    if cfg.ai_provider == "template":
        return TemplateProvider()

    try:
        return GeminiProvider(cfg.gemini_api_key, cfg.gemini_model)
    except RuntimeError as exc:
        print(f"[script] {exc}")
        print("[script] falling back to the offline template provider.")
        return TemplateProvider()
