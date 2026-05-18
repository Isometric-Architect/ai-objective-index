# Security Policy

## Supported Versions

AOI is in package-0 planning status. No production MCP server, public API, crawler, account system, or write-capable integration is implemented yet.

## Reporting A Vulnerability

Open a private security advisory or contact the project maintainers through the repository's preferred security channel once configured. Do not include secrets, access tokens, private customer data, or exploit instructions in public issues.

## v0.1 Security Boundary

v0.1 is read-only and contract-first. It must not execute payments, bookings, purchases, login flows, email sending, form submissions, or contract signing.

## Data Boundary

Sample files use fake but realistic objects and mock traces. Future real-data ingestion should preserve source URLs, retrieval timestamps, missing fields, and confidence values so users can understand evidence coverage.

