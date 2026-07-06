FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY samples ./samples

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir .

RUN mkdir -p /app/outputs

ENTRYPOINT ["python", "-m", "meeting_minutes_agent"]
CMD ["--help"]
