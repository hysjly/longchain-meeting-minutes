# LangChain 语音转会议纪要 Agent

本项目把 FunASR 结构化逐字稿转换为中文结构化会议纪要。第一版使用 LangChain 的 OpenAI-compatible chat model 接入小米 MiMo Token Plan，流程分为两次模型调用：

1. 说话人/角色推断与逐字稿标准化。
2. 基于标准化逐字稿生成 Markdown 会议纪要。

## 首次本地安装

建议使用 Python 3.12。在项目根目录运行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
notepad .env
```

编辑 `.env`，把示例占位符替换成真实有效的 MiMo Token Plan key：

```env
MIMO_API_KEY=你的真实有效key
MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro
LLM_PROVIDER=openai_compatible
```

不要把 `.env` 提交到 Git。

## 关闭窗口后重新运行

如果所有 PowerShell/终端窗口都关闭了，只需要重新进入项目目录并激活虚拟环境，不需要重新安装依赖：

```powershell
cd C:\Users\admin\Documents\LongChain语音转会议纪要
.\.venv\Scripts\Activate.ps1
```

看到命令行前面出现 `(.venv)` 后，就可以运行文字稿转会议纪要：

```powershell
python -m meeting_minutes_agent run samples\done_text.json -o outputs\minutes.md
```

运行过程中终端会显示两个阶段的进度条：`说话人角色推断中` 和 `会议纪要生成中`。

运行之前如果还没有填写 `.env`，先执行：

```powershell
notepad .env
```

确认 `MIMO_API_KEY` 不是 `replace-with-your-token-plan-key`，而是真实有效 key。

## 样例运行

当前 `samples` 目录里有三个样例：

- `samples\done_text.json`：第一种 `done/text` 输入格式。
- `samples\family_care_done_text.json`：把整段逐字稿都放在 `text` 字段里的样例。
- `samples\speaker_transcript.json`：未来带说话人分段的 `transcript[]` 输入格式。

生成普通样例纪要：

```powershell
python -m meeting_minutes_agent run samples\done_text.json -o outputs\minutes.md
```

生成家庭对话样例纪要：

```powershell
python -m meeting_minutes_agent run samples\family_care_done_text.json -o outputs\family_care_minutes.md
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

## 常见报错

`MIMO_API_KEY is required`：

说明没有 `.env`，或者 `.env` 里没有 `MIMO_API_KEY`。

`MIMO_API_KEY is still the example placeholder`：

说明 `.env` 里仍然是示例占位符，需要替换成真实 key。

`401 Invalid API Key`：

说明程序已经请求到 MiMo 服务，但服务端判定 key 无效。请在 MiMo 后台重新生成有效 key，并更新 `.env`。

## 切换到本地大模型

后续切换本地大模型时，如果本地服务兼容 OpenAI Chat Completions，只需要修改 `.env`：

```env
MIMO_BASE_URL=http://127.0.0.1:8000/v1
MIMO_MODEL=你的本地模型名
MIMO_API_KEY=本地服务需要的key或占位key
```

## Docker 部署运行

这套 Docker 配置适合你用 MobaXterm SSH 到公司 Linux 服务器后运行。假设代码已经上传到服务器项目目录，先进入项目目录：

```bash
cd /path/to/LongChain语音转会议纪要
```

服务器上准备 `.env`：

```bash
cp .env.example .env
nano .env
```

把 `MIMO_API_KEY` 改成真实有效 key。`.env` 不会被打进镜像，运行时由 `docker compose` 注入容器。

注意：`docker compose config` 会把 `.env` 里的环境变量展开到终端输出里，不要把它的完整输出贴到公开位置。

首次构建镜像：

```bash
docker compose build
```

运行默认样例，生成 `outputs/minutes.md`：

```bash
docker compose up --abort-on-container-exit
```

如果只想看一次性运行日志，也可以用：

```bash
docker compose run --rm meeting-minutes-agent run samples/done_text.json -o outputs/minutes.md
```

运行家庭对话样例：

```bash
docker compose run --rm meeting-minutes-agent run samples/family_care_done_text.json -o outputs/family_care_minutes.md
```

输出文件会保存在服务器项目目录的 `outputs/` 下。查看结果：

```bash
cat outputs/minutes.md
```

如果你把新的逐字稿 JSON 放到服务器项目目录的 `samples/your_transcript.json`，运行：

```bash
docker compose run --rm meeting-minutes-agent run samples/your_transcript.json -o outputs/your_minutes.md
```

后续代码更新后，重新构建再运行：

```bash
docker compose build --no-cache
docker compose run --rm meeting-minutes-agent run samples/done_text.json -o outputs/minutes.md
```

## 开发验证

```powershell
pytest -q --basetemp .pytest-tmp
```
