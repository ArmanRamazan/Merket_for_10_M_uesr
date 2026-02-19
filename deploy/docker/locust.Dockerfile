FROM python:3.12-slim

ADD https://astral.sh/uv/install.sh /tmp/uv-install.sh
RUN sh /tmp/uv-install.sh && mv /root/.local/bin/uv /bin/uv && rm /tmp/uv-install.sh

WORKDIR /app

RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv locust

ENV PATH="/app/.venv/bin:$PATH"

COPY tools/locust/ .

EXPOSE 8089

CMD ["locust", "-f", "locustfile.py"]
