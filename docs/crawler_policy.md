# Crawler Policy

Package 6A adds a crawler/extractor skeleton for future public-data acquisition. It does not run broad live crawling in v0.2 skeleton form.

## Scope

- Public pages only.
- Robots.txt must be respected before any future live fetch.
- Network fetching is disabled by default.
- Local tests and demos use fixtures only.
- User agent: `AI-Objective-Index-Bot/0.1`.

## Forbidden Sources And Actions

The crawler must not access:

- login-gated pages;
- paywalled pages;
- private data;
- personal account pages;
- supplier dashboards;
- forms that mutate state;
- payment, booking, purchase, or contract workflows.

The crawler must not perform:

- login;
- email sending;
- form submission;
- payment;
- booking;
- purchase;
- contract signing;
- account connection;
- supplier claim or verification.

## Rate Limits

Future live fetches should use conservative per-domain rate limiting. Package 6A includes a simple `RateLimiter`, but tests do not sleep or fetch network resources.

## Robots.txt

The Package 6A parser supports a small subset of `User-agent` and `Disallow` rules. Missing robots text is treated conservatively by the low-level policy helper.

## Opt-Out And Delete Requests

A future real-data package should define an opt-out and delete request path before any broad acquisition is enabled. Package 6A only prepares local fixture mechanics.

