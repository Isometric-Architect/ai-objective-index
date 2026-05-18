# Source Trace Methodology

Source traces make AOI rankings inspectable. A trace connects an object field to a source URL, title, snippet, retrieval time, and confidence value.

## What A Trace Can Support

A source trace may support claims such as:

- a tool has an API reference page;
- a pricing page mentions a free tier;
- terms mention commercial-use permissions;
- docs describe OCR, transcription, embeddings, monitoring, or other capabilities;
- an open-source repository appears active at retrieval time.

## What A Trace Cannot Prove

A trace does not prove that:

- the product is high quality;
- the source is complete or current;
- a legal, financial, medical, compliance, purchasing, or procurement decision is safe;
- a user should buy, book, pay, sign, submit, log in, or send anything.

## Required Fields

Each trace should include:

- `trace_id`;
- `object_id`;
- `field`;
- `source_url`;
- `source_title`;
- `source_snippet`;
- `retrieved_at`;
- `confidence`.

## Confidence

Use confidence to describe how directly the source supports the field:

- `0.90-1.00`: direct official source support;
- `0.70-0.89`: strong but partial support;
- `0.50-0.69`: indirect support or unclear wording;
- below `0.50`: weak support that should usually become a warning.

