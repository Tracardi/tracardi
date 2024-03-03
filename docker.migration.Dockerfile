FROM python:3.10-slim-buster

WORKDIR /app

RUN pip install --no-cache-dir aiomysql sqlalchemy alembic PyYAML==6.0 pydantic

COPY alembic.ini alembic.ini
COPY migrations migrations
COPY tracardi tracardi

RUN pwd
ENV PYTHONPATH "${PYTHONPATH}:/app/tracardi"

ENTRYPOINT ["alembic", "upgrade", "head"]