#!/bin/sh

openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048 > /dev/null 2>&1
openssl rsa -pubout -in private_key.pem -out public_key.pem > /dev/null 2>&1

PRIVATE_KEY_BASE64=$(openssl base64 -in private_key.pem | tr -d '\n')
PUBLIC_KEY_BASE64=$(openssl base64 -in public_key.pem | tr -d '\n')

echo "Public key (Base64):"
echo "$PUBLIC_KEY_BASE64"

rm private_key.pem public_key.pem
