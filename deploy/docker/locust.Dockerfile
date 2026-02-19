FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv locust

ENV PATH="/app/.venv/bin:$PATH"

COPY tools/locust/ .

EXPOSE 8089

CMD ["locust", "-f", "locustfile.py"]
