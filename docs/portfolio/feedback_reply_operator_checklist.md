# Feedback Reply Operator Checklist

- Save the reply as a local text or Markdown file.
- Do not include tokens, passwords, private keys, `.env` content, raw PII, raw private datasets, credentials, or private kernel details.
- Run `python -m ai_objective_index.portfolio.feedback_reply_intake --input <local_reply_file>`.
- Inspect the redaction report.
- Inspect the classification and route.
- Do not create GitHub issues, post comments, call APIs, fetch URLs, upload, merge, deploy, or publish automatically.
- Create a second-run only if the reply is local, redacted, and consent-bounded.
