#!/bin/sh

set -e

if [ -z "$PRIVATE_KEY" ]; then
  echo "PRIVATE_KEY is not set. Generating new keys..."

  KEYS_OUTPUT=$(sh /scripts/generate_keys.sh)
  PRIVATE_KEY=$(echo "$KEYS_OUTPUT" | grep 'Private key (Base64):' -A 1 | tail -n 1 | tr -d ' ')

  PUBLIC_KEY=$(echo "$KEYS_OUTPUT" | grep 'Public key (Base64):' -A 1 | tail -n 1 | tr -d ' ')

  echo "Public Key (Base64):"
  echo "$PUBLIC_KEY"

  export PRIVATE_KEY
  unset PUBLIC_KEY
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000 --no-access-log
