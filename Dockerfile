FROM python:3.13-alpine AS builder

RUN apk update && apk add --no-cache build-base libffi-dev postgresql-dev

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

FROM python:3.13-alpine

RUN apk update && apk add --no-cache libffi openssl

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src /app
COPY scripts/generate_keys.sh /scripts/generate_keys.sh
COPY scripts/entrypoint.sh /scripts/entrypoint.sh

RUN chmod +x /scripts/generate_keys.sh /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]

ENV DEBUG false

EXPOSE 8000
