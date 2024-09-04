FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE="false"

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock docker/entrypoint.sh ./
RUN poetry install --no-interaction --no-ansi --no-dev

COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY app /app/app

EXPOSE 8000

CMD ["export", "PYTHONPATH=/app"]
RUN ["chmod", "+x", "entrypoint.sh"]

ENTRYPOINT ["./entrypoint.sh"]