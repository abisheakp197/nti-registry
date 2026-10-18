# Security Policy

## Reporting a Vulnerability

If you discover a potential security vulnerability within `nti-registry`, please report it responsibly.

**Do NOT open a public issue on GitHub for security vulnerabilities.**

Instead, please send an email to:
`security@nti-cert.org` or `abisheakp197@gmail.com`

Include as much detail as possible, including:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)

## Response Timeline

- **Acknowledgement**: Within 24 hours.
- **Assessment & Fix**: Within 72 hours for Critical/High severity vulnerabilities.
- **Public Disclosure**: Coordinated after fix deployment.

## Security Architecture

- **Dilithium5 Cryptographic Proofs**: All registered entries are Dilithium5-signed.
- **Cross-Verification**: Entries are cross-verified against live badge nodes before storage.
- **Fail Closed Design**: Malformed requests, tampered payloads, or missing signatures are rejected with 400 Bad Request.
- **Payload Limits**: Ingestion payload sizes are strictly capped at 1MB (413 Payload Too Large).
- **Zero Information Leakage**: Exception stack traces and internal paths are never returned in HTTP responses.
