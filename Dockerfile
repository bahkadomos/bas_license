FROM python:3.13-alpine AS builder

RUN apk update && apk add --no-cache build-base libffi-dev postgresql-dev

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt

FROM python:3.13-alpine

RUN apk update && apk add --no-cache libffi

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src /app/src
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

EXPOSE 8000
