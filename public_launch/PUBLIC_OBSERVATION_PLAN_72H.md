# Public Observation Plan: First 72 Hours

## First 1 Hour

- Open the GitHub README: https://github.com/Isometric-Architect/ai-objective-index
- Open the Hugging Face Space: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Open the Hugging Face Dataset: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- Run the sample query: `browser automation MCP server`.
- Confirm the result shows source traces or limitations.
- Confirm the public pages still say not verified, not security certified, not a quality guarantee, and read-only.

## First 24 Hours

- Watch GitHub stars, issues, and clone signals if visible.
- Watch Hugging Face likes, downloads, and Space runs if visible.
- Check whether any issue reports include failed queries, wrong fields, missing traces, install failures, or docs confusion.
- Do not overreact to weak early signal.

## First 72 Hours

- Collect failures into GitHub Issues.
- Reproduce issues locally before patching.
- Patch only clear bugs, broken docs, missing source traces, or obviously confusing language.
- Add valid failures to golden queries before changing ranking behavior.
- Do not post communities until the public URLs, issue loop, and claim wording are stable.

## What Counts As Signal

- GitHub star, issue, clone/download, Hugging Face Space run, Hugging Face Dataset download, failed query report, missing source trace report, or install failure.

## What Does Not Count

- No immediate attention does not mean failure.
- A high rank is not a quality guarantee.
- A registry metadata candidate is not verification, security certification, or action permission.
