#!/bin/bash

# Create SSL directory if it doesn't exist
mkdir -p ./certs

# Generate SSL key and certificate
openssl req -x509 \
    -nodes \
    -days 365 \
    -newkey rsa:2048 \
    -keyout ./certs/stream.key \
    -out ./certs/stream.crt \
    -config ./config/cert.conf

echo "SSL certificates generated successfully!"