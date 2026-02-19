FROM python:3.12-slim

ADD https://astral.sh/uv/install.sh /tmp/uv-install.sh
RUN sh /tmp/uv-install.sh && mv /root/.local/bin/uv /bin/uv && rm /tmp/uv-install.sh

WORKDIR /app

RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv asyncpg faker

ENV PATH="/app/.venv/bin:$PATH"

COPY tools/seed/ .

CMD ["python", "seed.py"]
