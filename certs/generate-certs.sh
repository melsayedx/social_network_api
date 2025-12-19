#!/bin/bash
# Generate self-signed certificates for local HTTPS development
# Run this script once to create certs in the certs/ directory

CERT_DIR="$(dirname "$0")"
cd "$CERT_DIR"

# Generate private key
openssl genrsa -out localhost.key 2048

# Generate certificate signing request
openssl req -new -key localhost.key -out localhost.csr -subj "/CN=localhost/O=SocialNetwork/C=US"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in localhost.csr -signkey localhost.key -out localhost.crt \
  -extfile <(printf "subjectAltName=DNS:localhost,IP:127.0.0.1")

# Clean up CSR
rm localhost.csr

echo "✅ Certificates generated:"
echo "   - certs/localhost.crt"
echo "   - certs/localhost.key"
echo ""
echo "To trust on macOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain localhost.crt"
