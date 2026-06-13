"""Load GEMINI_API_KEY from ~/.hermes/.env or environment."""

from __future__ import annotations

import os
from pathlib import Path


def load_gemini_api_key() -> str:
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        val = os.environ.get(key, "").strip()
        if val:
            return val

    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            name = name.strip()
            if name in ("GEMINI_API_KEY", "GOOGLE_API_KEY") and value.strip():
                return value.strip().strip('"').strip("'")

    raise RuntimeError(
        "No Gemini API key found. Set GEMINI_API_KEY in ~/.hermes/.env or the environment."
    )
