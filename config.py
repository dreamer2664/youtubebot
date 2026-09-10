"""Configuration loading with environment-variable overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULTS: dict[str, Any] = {
    "channel": {
        "topic": "unusual true stories from maritime history",
        "tone": "calm, factual, quietly dramatic",
        "audience": "curious adults who like short documentary-style videos",
        "target_seconds": 150,
        "voice": "en-GB-RyanNeural",
        "language": "English",
        "category_id": "22",
        "default_tags": [],
    },
    "video": {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "zoom": 1.12,
        "transition": 0.5,
    },
    "privacy": {
        "status": "private",
        "audit_passed": False,
        "max_uploads_per_run": 3,
    },
    "ai": {
        "provider": "gemini",
        "gemini_api_key": "",
        "gemini_model": "gemini-flash-latest",
        "image_provider": "pollinations",
        "image_width": 1280,
        "image_height": 720,
        "image_timeout": 90,
    },
    "paths": {
        "work_dir": "work",
        "out_dir": "out",
        "state_file": "state.json",
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in (override or {}).items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


@dataclass
class Config:
    root: Path
    data: dict[str, Any]

    # -- channel ---------------------------------------------------------
    @property
    def topic(self) -> str:
        return self.data["channel"]["topic"]

    @property
    def tone(self) -> str:
        return self.data["channel"]["tone"]

    @property
    def audience(self) -> str:
        return self.data["channel"]["audience"]

    @property
    def target_seconds(self) -> int:
        return int(self.data["channel"]["target_seconds"])

    @property
    def voice(self) -> str:
        return self.data["channel"]["voice"]

    @property
    def language(self) -> str:
        return self.data["channel"]["language"]

    @property
    def category_id(self) -> str:
        return str(self.data["channel"]["category_id"])

    @property
    def default_tags(self) -> list[str]:
        return list(self.data["channel"].get("default_tags") or [])

    # -- video -----------------------------------------------------------
    @property
    def width(self) -> int:
        return int(self.data["video"]["width"])

    @property
    def height(self) -> int:
        return int(self.data["video"]["height"])

    @property
    def fps(self) -> int:
        return int(self.data["video"]["fps"])

    @property
    def zoom(self) -> float:
        return float(self.data["video"]["zoom"])

    @property
    def transition(self) -> float:
        return float(self.data["video"]["transition"])

    # -- privacy ---------------------------------------------------------
    @property
    def privacy_status(self) -> str:
        return str(self.data["privacy"]["status"]).lower()

    @property
    def audit_passed(self) -> bool:
        return bool(self.data["privacy"]["audit_passed"])

    @property
    def max_uploads_per_run(self) -> int:
        return int(self.data["privacy"]["max_uploads_per_run"])

    # -- ai --------------------------------------------------------------
    @property
    def ai_provider(self) -> str:
        return str(self.data["ai"]["provider"]).lower()

    @property
    def gemini_api_key(self) -> str:
        return (
            os.environ.get("GEMINI_API_KEY")
            or str(self.data["ai"].get("gemini_api_key") or "")
        ).strip()

    @property
    def gemini_model(self) -> str:
        return str(self.data["ai"]["gemini_model"])

    @property
    def image_width(self) -> int:
        return int(self.data["ai"]["image_width"])

    @property
    def image_height(self) -> int:
        return int(self.data["ai"]["image_height"])

    @property
    def image_timeout(self) -> int:
        return int(self.data["ai"]["image_timeout"])

    # -- paths -----------------------------------------------------------
    @property
    def work_dir(self) -> Path:
        return self.root / self.data["paths"]["work_dir"]

    @property
    def out_dir(self) -> Path:
        return self.root / self.data["paths"]["out_dir"]

    @property
    def state_file(self) -> Path:
        return self.root / self.data["paths"]["state_file"]

    @property
    def client_secret_file(self) -> Path:
        return self.root / "client_secret.json"

    @property
    def token_file(self) -> Path:
        return self.root / "token.json"

    def ensure_dirs(self) -> None:
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)


def load_config(path: str | os.PathLike | None = None) -> Config:
    """Load config.yaml, falling back to bundled defaults."""
    root = Path(path).resolve().parent if path else Path.cwd().resolve()
    cfg_path = Path(path) if path else root / "config.yaml"

    data = DEFAULTS
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as handle:
            user = yaml.safe_load(handle) or {}
        data = _deep_merge(DEFAULTS, user)

    cfg = Config(root=root, data=data)
    cfg.ensure_dirs()
    return cfg
