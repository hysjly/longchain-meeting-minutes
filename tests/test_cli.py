from typer.testing import CliRunner

from meeting_minutes_agent.cli import app


def test_cli_run_writes_output_file(tmp_path, monkeypatch):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.md"
    input_path.write_text('{"recordId":"abc","text":"今天讨论排期。"}', encoding="utf-8")

    monkeypatch.setattr(
        "meeting_minutes_agent.cli.generate_minutes",
        lambda payload: "# 会议纪要\n\n## 会议概览\n- 测试。\n",
    )

    result = CliRunner().invoke(app, ["run", str(input_path), "-o", str(output_path)])

    assert result.exit_code == 0
    assert output_path.read_text(encoding="utf-8").startswith("# 会议纪要")


def test_cli_run_prints_stdout_when_output_is_omitted(tmp_path, monkeypatch):
    input_path = tmp_path / "input.json"
    input_path.write_text('{"recordId":"abc","text":"今天讨论排期。"}', encoding="utf-8")

    monkeypatch.setattr(
        "meeting_minutes_agent.cli.generate_minutes",
        lambda payload: "# 会议纪要\n\n## 会议概览\n- 测试。\n",
    )

    result = CliRunner().invoke(app, ["run", str(input_path)])

    assert result.exit_code == 0
    assert "# 会议纪要" in result.stdout


def test_cli_run_shows_concise_configuration_error(tmp_path, monkeypatch):
    input_path = tmp_path / "input.json"
    input_path.write_text('{"recordId":"abc","text":"今天讨论排期。"}', encoding="utf-8")

    def raise_config_error(payload):
        raise ValueError("MIMO_API_KEY is required for OpenAI-compatible MiMo calls.")

    monkeypatch.setattr("meeting_minutes_agent.cli.generate_minutes", raise_config_error)

    result = CliRunner().invoke(app, ["run", str(input_path)])

    assert result.exit_code == 1
    assert "MIMO_API_KEY is required" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_run_shows_concise_provider_error(tmp_path, monkeypatch):
    input_path = tmp_path / "input.json"
    input_path.write_text('{"recordId":"abc","text":"今天讨论排期。"}', encoding="utf-8")

    ProviderAuthenticationError = type(
        "AuthenticationError",
        (Exception,),
        {"__module__": "openai"},
    )

    def raise_provider_error(payload):
        raise ProviderAuthenticationError("Error code: 401 - Invalid API Key")

    monkeypatch.setattr("meeting_minutes_agent.cli.generate_minutes", raise_provider_error)

    result = CliRunner().invoke(app, ["run", str(input_path)])

    assert result.exit_code == 1
    assert "LLM provider error" in result.stderr
    assert "Invalid API Key" in result.stderr
    assert "Traceback" not in result.stderr
