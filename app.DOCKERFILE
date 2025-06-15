FROM python:3.12-slim-bookworm AS builder

ENV POETRY_VERSION=2.1.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

RUN apt-get update && apt-get install -y build-essential curl libpq-dev

RUN curl -sSL https://install.python-poetry.org | python -

RUN mkdir -p /app
WORKDIR /app

COPY dda/ /app/dda/
COPY manage.py poetry.lock pyproject.toml /app/

RUN poetry install --only main

RUN addgroup --system dda && adduser --system --ingroup dda dda-user

FROM builder AS runtime

COPY --from=builder /app /app
RUN chown -R dda-user:dda /app

WORKDIR /app
USER dda-user

CMD ["uvicorn", "dda.asgi:application", "--host", "0.0.0.0", "--port", "9000", "--lifespan", "off"]
