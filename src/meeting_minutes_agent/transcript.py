from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from meeting_minutes_agent.models import (
    TranscriptDocument,
    TranscriptInputError,
    TranscriptSegment,
)


def adapt_transcript(payload: dict[str, Any]) -> TranscriptDocument:
    if not isinstance(payload, dict):
        raise TranscriptInputError("Transcript input must be a JSON object.")

    segments = _segments_from_transcript(payload) or _segments_from_text(payload)
    if not segments:
        raise TranscriptInputError("Transcript input must include text or transcript.")

    return TranscriptDocument(
        record_id=payload.get("recordId") or payload.get("record_id"),
        duration=_optional_float(payload.get("duration")),
        audio_url=payload.get("audioUrl") or payload.get("audio_url"),
        segments=segments,
        raw=payload,
    )


def chunk_segments(
    segments: Sequence[TranscriptSegment],
    max_chars: int = 6000,
) -> list[list[TranscriptSegment]]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive.")

    chunks: list[list[TranscriptSegment]] = []
    current: list[TranscriptSegment] = []
    current_chars = 0

    for segment in segments:
        segment_chars = len(segment.text)
        if current and current_chars + segment_chars > max_chars:
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(segment)
        current_chars += segment_chars

    if current:
        chunks.append(current)

    return chunks


def render_segments(segments: Iterable[TranscriptSegment]) -> str:
    lines = []
    for index, segment in enumerate(segments, start=1):
        label = segment.inferred_role or segment.speaker
        time_range = _format_time_range(segment)
        notes = f" notes={segment.notes}" if segment.notes else ""
        lines.append(f"[S{index}] {time_range}{label}: {segment.text}{notes}".strip())
    return "\n".join(lines)


def _segments_from_text(payload: dict[str, Any]) -> list[TranscriptSegment]:
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return []
    return [
        TranscriptSegment(
            speaker="Speaker 1",
            text=text.strip(),
            start=None,
            end=_optional_float(payload.get("duration")),
            confidence=None,
            notes="source: text",
        )
    ]


def _segments_from_transcript(payload: dict[str, Any]) -> list[TranscriptSegment]:
    transcript = payload.get("transcript")
    if transcript is None:
        return []
    if not isinstance(transcript, list):
        raise TranscriptInputError("transcript must be a list of segment objects.")

    segments: list[TranscriptSegment] = []
    for index, item in enumerate(transcript, start=1):
        if not isinstance(item, dict):
            raise TranscriptInputError(f"transcript[{index}] must be an object.")
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise TranscriptInputError(f"transcript[{index}].text is required.")
        speaker = item.get("speaker") or f"Speaker {index}"
        segments.append(
            TranscriptSegment(
                speaker=str(speaker),
                start=_optional_float(item.get("start")),
                end=_optional_float(item.get("end")),
                text=text.strip(),
                confidence=_optional_float(item.get("confidence")),
                notes="source: transcript",
            )
        )
    return segments


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _format_time_range(segment: TranscriptSegment) -> str:
    if segment.start is None and segment.end is None:
        return ""
    start = "" if segment.start is None else f"{segment.start:.2f}"
    end = "" if segment.end is None else f"{segment.end:.2f}"
    return f"{start}-{end} "
