from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-pro"
DEFAULT_PROVIDER = "openai_compatible"
PLACEHOLDER_API_KEYS = {"replace-with-your-token-plan-key"}


@dataclass(frozen=True, slots=True)
class LLMSettings:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    provider: str = DEFAULT_PROVIDER
    temperature: float = 0.2
    transcript_chunk_chars: int = 6000


def load_settings() -> LLMSettings:
    load_dotenv()
    api_key = os.getenv("MIMO_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("MIMO_API_KEY is required for OpenAI-compatible MiMo calls.")
    if api_key.strip() in PLACEHOLDER_API_KEYS:
        raise ValueError("MIMO_API_KEY is still the example placeholder; replace it with a valid MiMo Token Plan key.")

    temperature_raw = os.getenv("LLM_TEMPERATURE", "0.2")
    chunk_chars_raw = os.getenv("TRANSCRIPT_CHUNK_CHARS", "6000")

    return LLMSettings(
        api_key=api_key,
        base_url=os.getenv("MIMO_BASE_URL", DEFAULT_BASE_URL),
        model=os.getenv("MIMO_MODEL", DEFAULT_MODEL),
        provider=os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER),
        temperature=float(temperature_raw),
        transcript_chunk_chars=int(chunk_chars_raw),
    )
