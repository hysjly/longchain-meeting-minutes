from __future__ import annotations

from typing import Any

from meeting_minutes_agent.config import LLMSettings


def create_chat_model(settings: LLMSettings) -> Any:
    if settings.provider != "openai_compatible":
        raise ValueError(f"Unsupported LLM_PROVIDER: {settings.provider}")

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "langchain-openai is required. Install dependencies with "
            "`python -m pip install -e .[dev]` inside the virtual environment."
        ) from exc

    return ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        temperature=settings.temperature,
    )
