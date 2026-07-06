from meeting_minutes_agent.chains import MinutesGenerationChain, SpeakerInferenceChain
from meeting_minutes_agent.models import TranscriptDocument, TranscriptSegment


class Response:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self, content):
        self.content = content
        self.messages = []

    def invoke(self, messages):
        self.messages.append(messages)
        return Response(self.content)


def test_speaker_inference_merges_roles_without_rewriting_text():
    llm = FakeLLM(
        '{"segments":[{"speaker":"Speaker 1","inferred_role":"王姐","text":"会前文本不应覆盖","notes":"称呼推断"}],"summary_notes":"王姐在推进排期。"}'
    )
    document = TranscriptDocument(
        record_id="abc",
        segments=[TranscriptSegment(speaker="Speaker 1", text="王姐，今天确认排期。")],
    )

    result = SpeakerInferenceChain(llm).infer(document, [document.segments])

    assert result.segments[0].speaker == "Speaker 1"
    assert result.segments[0].inferred_role == "王姐"
    assert result.segments[0].text == "王姐，今天确认排期。"
    assert result.summary_notes == "王姐在推进排期。"


def test_minutes_generation_requires_standard_markdown_sections():
    markdown = (
        "## 会议概览\n- 测试\n\n"
        "## 核心结论\n- 结论\n\n"
        "## 议题讨论\n- 讨论\n\n"
        "## 行动项\n| 事项 | 负责人 | 截止时间 | 状态 |\n"
        "| --- | --- | --- | --- |\n"
        "| 提交方案 | 未明确 | 未明确 | 待办 |\n\n"
        "## 风险与待确认\n- 无\n\n"
        "## 原文引用索引\n- [S1] 测试"
    )
    llm = FakeLLM(markdown)
    document = TranscriptDocument(
        record_id="abc",
        segments=[TranscriptSegment(speaker="Speaker 1", text="今天确认排期。")],
    )
    inference = SpeakerInferenceChain(
        FakeLLM(
            '{"segments":[{"speaker":"Speaker 1","inferred_role":"项目经理","text":"今天确认排期。","notes":""}],"summary_notes":""}'
        )
    ).infer(document, [document.segments])

    result = MinutesGenerationChain(llm).generate(document, inference)

    assert "## 会议概览" in result
    assert "## 行动项" in result
    assert "未明确" in result
    assert "不要编造" in llm.messages[0][0][1]
