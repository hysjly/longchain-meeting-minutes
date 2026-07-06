from __future__ import annotations

from typing import Any

from meeting_minutes_agent.config import load_settings
from meeting_minutes_agent.llm import create_chat_model
from meeting_minutes_agent.chains import MinutesGenerationChain, SpeakerInferenceChain
from meeting_minutes_agent.models import InferenceResult, TranscriptDocument
from meeting_minutes_agent.transcript import adapt_transcript, chunk_segments


def generate_minutes(
    input_data: dict[str, Any],
    *,
    speaker_chain: Any | None = None,
    minutes_chain: Any | None = None,
) -> str:
    document = adapt_transcript(input_data)

    if speaker_chain is None or minutes_chain is None:
        settings = load_settings()
        llm = create_chat_model(settings)
        speaker_chain = speaker_chain or SpeakerInferenceChain(llm)
        minutes_chain = minutes_chain or MinutesGenerationChain(llm)
        max_chars = settings.transcript_chunk_chars
    else:
        max_chars = 6000

    chunks = chunk_segments(document.segments, max_chars=max_chars)
    inference = speaker_chain.infer(document, chunks)
    markdown = minutes_chain.generate(document, inference)

    return _with_metadata_front_matter(document, inference, markdown)


def _with_metadata_front_matter(
    document: TranscriptDocument,
    inference: InferenceResult,
    markdown: str,
) -> str:
    lines = ["---"]
    if document.record_id is not None:
        lines.append(f"recordId: {document.record_id}")
    if document.duration is not None:
        lines.append(f"duration: {document.duration:g}")
    if document.audio_url is not None:
        lines.append(f"audioUrl: {document.audio_url}")
    lines.append(f"segments: {len(inference.segments)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + markdown.strip() + "\n"
