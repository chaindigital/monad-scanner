FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/pyproject.toml
RUN pip install -U pip && pip install -e .

COPY src /app/src
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

EXPOSE 8080

CMD ["python", "-m", "scanner.main"]
