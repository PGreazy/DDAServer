FROM python:3.12 AS builder

ENV POETRY_VERSION=2.1.2
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y build-essential

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry config virtualenvs.in-project true

RUN mkdir -p /app
WORKDIR /app
COPY . .

RUN poetry env use python3.12 && poetry install --only main

FROM python:3.12-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app /app

WORKDIR /app

CMD ["python", "-m", "uvicorn", "dda.asgi:application", "--host", "0.0.0.0", "--port", "9000", "--lifespan", "off"]
