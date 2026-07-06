from meeting_minutes_agent.models import InferenceResult, TranscriptSegment
from meeting_minutes_agent.service import generate_minutes


class FakeSpeakerInference:
    def infer(self, document, chunks):
        return InferenceResult(
            segments=[
                TranscriptSegment(
                    speaker="Speaker 1",
                    inferred_role="host",
                    text="discuss schedule",
                )
            ],
            summary_notes="speaker inferred",
        )


class FakeMinutesGenerator:
    def generate(self, document, inference):
        return "# minutes\n"


def test_generate_minutes_reports_two_llm_progress_stages():
    events = []

    generate_minutes(
        {"recordId": "abc", "text": "discuss schedule"},
        speaker_chain=FakeSpeakerInference(),
        minutes_chain=FakeMinutesGenerator(),
        progress_callback=events.append,
    )

    assert events == [
        "speaker_inference_start",
        "speaker_inference_done",
        "minutes_generation_start",
        "minutes_generation_done",
    ]
