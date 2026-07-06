from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TranscriptInputError(ValueError):
    """Raised when FunASR transcript input cannot be adapted."""


class TranscriptSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    speaker: str = Field(min_length=1)
    text: str = Field(min_length=1)
    start: float | None = None
    end: float | None = None
    confidence: float | None = None
    inferred_role: str | None = None
    notes: str | None = None


class TranscriptDocument(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    segments: list[TranscriptSegment]
    record_id: str | None = None
    duration: float | None = None
    audio_url: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class InferenceResult(BaseModel):
    segments: list[TranscriptSegment]
    summary_notes: str = ""
