# LangChain 语音转会议纪要 Agent

本项目把 FunASR 结构化逐字稿转换为中文结构化会议纪要。第一版使用 LangChain 的 OpenAI-compatible chat model 接入小米 MiMo Token Plan，流程分为两次模型调用：

1. 说话人/角色推断与逐字稿标准化。
2. 基于标准化逐字稿生成 Markdown 会议纪要。

## 本地运行

建议使用 Python 3.12：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

编辑 `.env`，填入你的 `MIMO_API_KEY`。不要把 `.env` 提交到 Git。

```powershell
python -m meeting_minutes_agent run samples\done_text.json -o outputs\minutes.md
```

不传 `-o` 时会直接输出到终端：

```powershell
python -m meeting_minutes_agent run samples\speaker_transcript.json
```

## 输入格式

当前 FunASR `done/text` 格式：

```json
{
  "type": "done",
  "recordId": "550e8400-e29b-41d4-a716-446655440000",
  "text": "今天天气真不错。",
  "duration": 12.34,
  "audioUrl": "/api/records/550e8400-e29b-41d4-a716-446655440000/audio"
}
```

后续带说话人格式：

```json
{
  "recordId": "meeting-001",
  "transcript": [
    {
      "speaker": "Speaker 1",
      "start": 1.02,
      "end": 1.46,
      "text": "王姐，",
      "confidence": null
    }
  ]
}
```

## 配置

`.env.example` 中的默认值适配 MiMo OpenAI-compatible 接口：

- `MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1`
- `MIMO_MODEL=mimo-v2.5-pro`
- `LLM_PROVIDER=openai_compatible`

后续切换本地大模型时，如果本地服务兼容 OpenAI Chat Completions，只需要把 `MIMO_BASE_URL`、`MIMO_MODEL` 和 key 改成对应配置。

## 开发验证

```powershell
pytest -q --basetemp .pytest-tmp
```
