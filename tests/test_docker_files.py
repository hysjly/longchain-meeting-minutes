from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_installs_project_and_runs_cli_module():
    dockerfile = ROOT / "Dockerfile"

    content = dockerfile.read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in content
    assert "pip install --no-cache-dir ." in content
    assert 'ENTRYPOINT ["python", "-m", "meeting_minutes_agent"]' in content


def test_compose_runs_done_text_sample_with_env_file_and_outputs_mount():
    compose = ROOT / "docker-compose.yml"

    content = compose.read_text(encoding="utf-8")

    assert "env_file:" in content
    assert "- .env" in content
    assert "./outputs:/app/outputs" in content
    assert "run" in content
    assert "samples/done_text.json" in content
    assert "outputs/minutes.md" in content


def test_dockerignore_excludes_secrets_and_local_artifacts():
    dockerignore = ROOT / ".dockerignore"

    content = dockerignore.read_text(encoding="utf-8")

    assert ".env" in content
    assert ".venv" in content
    assert "__pycache__" in content
    assert ".git" in content
