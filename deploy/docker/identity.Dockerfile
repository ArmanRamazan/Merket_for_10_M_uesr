FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY libs/py/common /libs/common

COPY services/py/identity/pyproject.toml .

RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv /libs/common \
    && uv pip install --python /app/.venv \
        "fastapi>=0.115" \
        "uvicorn>=0.34" \
        "asyncpg>=0.30" \
        "bcrypt>=4.0" \
        "pyjwt>=2.10" \
        "pydantic-settings>=2.7" \
        "email-validator>=2.0" \
        "prometheus-fastapi-instrumentator>=7.0"

ENV PATH="/app/.venv/bin:$PATH"

COPY services/py/identity/ .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
