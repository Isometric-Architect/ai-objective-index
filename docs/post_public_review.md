# Post-Public Review

After a public visibility switch, manually verify the public URLs before posting any announcement.

## Checklist

1. Open the GitHub URL in an incognito/private browser.
2. Confirm README renders.
3. Open the Hugging Face Space URL.
4. Run sample query: `browser automation MCP server`.
5. Open the Hugging Face Dataset URL.
6. Confirm the Dataset Card says not verified, not security certified, and not a quality guarantee.
7. Confirm issue templates are visible.
8. Confirm no token or secret appears.
9. Do not post a community message until separately decided.

## Commands

```powershell
python -m ai_objective_index.public_url_qa
python -m ai_objective_index.post_public_state_report
```

## Boundaries

Public review is URL and wording QA. It is not security certification, supplier verification, quality assurance, production readiness, or purchasing advice.
