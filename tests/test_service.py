from meeting_minutes_agent.models import InferenceResult, TranscriptSegment
from meeting_minutes_agent.service import generate_minutes


class FakeSpeakerInference:
    def infer(self, document, chunks):
        assert document.record_id == "abc"
        assert len(chunks) == 1
        return InferenceResult(
            segments=[
                TranscriptSegment(
                    speaker="Speaker 1",
                    inferred_role="王姐",
                    start=None,
                    end=None,
                    text="王姐，今天确认排期。",
                    confidence=None,
                    notes="称呼明确",
                )
            ],
            summary_notes="王姐负责推进排期。",
        )


class FakeMinutesGenerator:
    def generate(self, document, inference):
        assert inference.segments[0].inferred_role == "王姐"
        return (
            "# 会议纪要\n\n"
            "## 会议概览\n- 讨论项目排期。\n\n"
            "## 核心结论\n- 下周三前提交方案。\n\n"
            "## 议题讨论\n- 王姐确认整体节奏。\n\n"
            "## 行动项\n"
            "| 事项 | 负责人 | 截止时间 | 状态 |\n"
            "| --- | --- | --- | --- |\n"
            "| 提交方案 | 未明确 | 下周三 | 待办 |\n\n"
            "## 风险与待确认\n- 负责人未明确。\n\n"
            "## 原文引用索引\n- [S1] 王姐，今天确认排期。\n"
        )


def test_generate_minutes_runs_speaker_inference_before_minutes_generation():
    markdown = generate_minutes(
        {
            "recordId": "abc",
            "text": "王姐，今天确认排期。",
            "duration": 20,
            "audioUrl": "/audio",
        },
        speaker_chain=FakeSpeakerInference(),
        minutes_chain=FakeMinutesGenerator(),
    )

    assert markdown.startswith("---\nrecordId: abc")
    assert "duration: 20" in markdown
    assert "audioUrl: /audio" in markdown
    assert "## 行动项" in markdown
    assert "未明确" in markdown
