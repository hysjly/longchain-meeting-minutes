import pytest
from pydantic import ValidationError

from meeting_minutes_agent.models import TranscriptInputError, TranscriptSegment
from meeting_minutes_agent.transcript import adapt_transcript, chunk_segments


def test_done_text_input_becomes_single_standard_segment():
    payload = {
        "type": "done",
        "recordId": "550e8400-e29b-41d4-a716-446655440000",
        "text": "王姐，今天我们讨论项目排期。小李，下周三前给我方案。",
        "duration": 12.34,
        "audioUrl": "/api/records/550e8400/audio",
    }

    document = adapt_transcript(payload)

    assert document.record_id == "550e8400-e29b-41d4-a716-446655440000"
    assert document.duration == 12.34
    assert document.audio_url == "/api/records/550e8400/audio"
    assert len(document.segments) == 1
    assert document.segments[0].speaker == "Speaker 1"
    assert document.segments[0].text == payload["text"]
    assert document.segments[0].notes == "source: text"


def test_transcript_array_preserves_speaker_timing_and_confidence():
    payload = {
        "recordId": "abc",
        "transcript": [
            {
                "speaker": "Speaker 1",
                "start": 1.02,
                "end": 1.46,
                "text": "王姐，",
                "confidence": None,
            },
            {
                "speaker": "Speaker 2",
                "start": 1.47,
                "end": 3.21,
                "text": "我下周三给方案。",
                "confidence": 0.91,
            },
        ],
    }

    document = adapt_transcript(payload)

    assert [segment.speaker for segment in document.segments] == ["Speaker 1", "Speaker 2"]
    assert document.segments[0].start == 1.02
    assert document.segments[0].end == 1.46
    assert document.segments[1].confidence == 0.91
    assert document.segments[1].text == "我下周三给方案。"


def test_missing_text_and_transcript_raises_clear_error():
    with pytest.raises(TranscriptInputError, match="text or transcript"):
        adapt_transcript({"type": "done", "recordId": "abc"})


def test_transcript_segment_validates_text_with_pydantic():
    with pytest.raises(ValidationError):
        TranscriptSegment(speaker="Speaker 1", text="")


def test_chunk_segments_respects_budget_without_losing_text():
    payload = {
        "transcript": [
            {"speaker": "Speaker 1", "text": "第一段内容很长。", "start": 0, "end": 1},
            {"speaker": "Speaker 2", "text": "第二段继续推进。", "start": 1, "end": 2},
            {"speaker": "Speaker 1", "text": "第三段收尾。", "start": 2, "end": 3},
        ]
    }
    document = adapt_transcript(payload)

    chunks = chunk_segments(document.segments, max_chars=12)

    assert len(chunks) == 3
    assert "".join(segment.text for chunk in chunks for segment in chunk) == (
        "第一段内容很长。第二段继续推进。第三段收尾。"
    )
