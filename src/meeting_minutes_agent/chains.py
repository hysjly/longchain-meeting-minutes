from __future__ import annotations

import json
from typing import Any

from meeting_minutes_agent.models import (
    InferenceResult,
    TranscriptDocument,
    TranscriptSegment,
)
from meeting_minutes_agent.transcript import render_segments


SPEAKER_SYSTEM_PROMPT = """你是会议逐字稿整理助手。请根据上下文尽量推断说话人的姓名、称呼或角色。
要求：
1. 不要改写原文 text。
2. 如果已有 speaker 标签，请保留原 speaker，并在 inferred_role 中给出推断出的姓名/角色。
3. 如果无法确定，inferred_role 使用原 speaker，notes 说明“不确定”。
4. 只输出 JSON，格式为 {"segments":[{"speaker":"...","inferred_role":"...","text":"...","notes":"..."}],"summary_notes":"..."}。
"""

MINUTES_SYSTEM_PROMPT = """你是专业中文会议纪要助手。请基于已整理的逐字稿生成结构化 Markdown 会议纪要。
必须包含以下二级标题：
## 会议概览
## 核心结论
## 议题讨论
## 行动项
## 风险与待确认
## 原文引用索引
行动项使用 Markdown 表格，列为：事项、负责人、截止时间、状态。负责人或截止时间不明确时写“未明确”。不要编造逐字稿没有支持的信息。
"""


class SpeakerInferenceChain:
    def __init__(self, llm: Any):
        self._llm = llm

    def infer(
        self,
        document: TranscriptDocument,
        chunks: list[list[TranscriptSegment]],
    ) -> InferenceResult:
        inferred_segments: list[TranscriptSegment] = []
        summary_notes: list[str] = []

        for chunk_index, chunk in enumerate(chunks, start=1):
            response_text = _invoke_text(
                self._llm,
                [
                    ("system", SPEAKER_SYSTEM_PROMPT),
                    (
                        "human",
                        "请整理以下会议逐字稿分块。"
                        f"\nrecordId: {document.record_id or '未提供'}"
                        f"\nchunk: {chunk_index}/{len(chunks)}"
                        f"\n\n{render_segments(chunk)}",
                    ),
                ],
            )
            parsed = _parse_json_response(response_text)
            summary = parsed.get("summary_notes")
            if isinstance(summary, str) and summary.strip():
                summary_notes.append(summary.strip())
            inferred_segments.extend(_merge_inferred_segments(chunk, parsed.get("segments")))

        return InferenceResult(
            segments=inferred_segments,
            summary_notes="\n".join(summary_notes),
        )


class MinutesGenerationChain:
    def __init__(self, llm: Any):
        self._llm = llm

    def generate(
        self,
        document: TranscriptDocument,
        inference: InferenceResult,
    ) -> str:
        response = _invoke_text(
            self._llm,
            [
                ("system", MINUTES_SYSTEM_PROMPT),
                (
                    "human",
                    "请生成会议纪要。"
                    f"\nrecordId: {document.record_id or '未提供'}"
                    f"\nduration: {document.duration if document.duration is not None else '未提供'}"
                    f"\naudioUrl: {document.audio_url or '未提供'}"
                    f"\nsummary_notes:\n{inference.summary_notes or '无'}"
                    f"\n\n逐字稿：\n{render_segments(inference.segments)}",
                ),
            ],
        )
        return response.strip()


def _invoke_text(llm: Any, messages: list[tuple[str, str]]) -> str:
    result = llm.invoke(messages)
    content = getattr(result, "content", result)
    if isinstance(content, list):
        return "\n".join(str(item) for item in content)
    return str(content)


def _parse_json_response(response_text: str) -> dict[str, Any]:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("Speaker inference model did not return valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Speaker inference JSON must be an object.")
    return parsed


def _merge_inferred_segments(
    source_segments: list[TranscriptSegment],
    inferred_items: Any,
) -> list[TranscriptSegment]:
    if not isinstance(inferred_items, list):
        return source_segments

    merged: list[TranscriptSegment] = []
    for index, source in enumerate(source_segments):
        item = inferred_items[index] if index < len(inferred_items) else {}
        if not isinstance(item, dict):
            item = {}
        merged.append(
            TranscriptSegment(
                speaker=str(item.get("speaker") or source.speaker),
                inferred_role=_optional_str(item.get("inferred_role")) or source.inferred_role,
                start=source.start,
                end=source.end,
                text=source.text,
                confidence=source.confidence,
                notes=_optional_str(item.get("notes")) or source.notes,
            )
        )
    return merged


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
