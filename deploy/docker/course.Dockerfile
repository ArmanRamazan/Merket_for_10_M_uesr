FROM python:3.12-slim

ADD https://astral.sh/uv/install.sh /tmp/uv-install.sh
RUN sh /tmp/uv-install.sh && mv /root/.local/bin/uv /bin/uv && rm /tmp/uv-install.sh

WORKDIR /app

COPY libs/py/common /libs/common

COPY services/py/course/pyproject.toml .

RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv /libs/common \
    && uv pip install --python /app/.venv \
        "fastapi>=0.115" \
        "uvicorn>=0.34" \
        "asyncpg>=0.30" \
        "pyjwt>=2.10" \
        "pydantic-settings>=2.7" \
        "prometheus-fastapi-instrumentator>=7.0"

ENV PATH="/app/.venv/bin:$PATH"

COPY services/py/course/ .

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
