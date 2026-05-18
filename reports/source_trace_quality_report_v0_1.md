# Source Trace Quality Report v0.1

Date: 2026-05-18

This is a v0.1 benchmark report based on sample/extracted records. It is not a quality guarantee, official ranking, legal advice, purchasing advice, or safety certification.

## What Is SourceTrace

`SourceTrace` connects an AOI object field to a source URL, title, snippet, retrieval timestamp, and confidence value.

## SourceTrace Coverage Summary

- Object-level trace coverage: 1.0
- Trace count: 20
- Objects: 20

## SourceRank Distribution

{'SourceRank.UNKNOWN': 20}

## Objects With Strongest Trace Coverage

| object_id | name | trace_count |
| --- | --- | --- |
| aoi-pixelforge-api | PixelForge API | 1 |
| aoi-clearscan-ocr-api | ClearScan OCR API | 1 |
| aoi-meetscribe-ai | MeetScribe AI | 1 |
| aoi-codepilot-studio | CodePilot Studio | 1 |
| aoi-searchmcp-relay | SearchMCP Relay | 1 |

## Objects With Weak Trace Coverage

| object_id | name | trace_count |
| --- | --- | --- |
| aoi-pixelforge-api | PixelForge API | 1 |
| aoi-clearscan-ocr-api | ClearScan OCR API | 1 |
| aoi-meetscribe-ai | MeetScribe AI | 1 |
| aoi-codepilot-studio | CodePilot Studio | 1 |
| aoi-searchmcp-relay | SearchMCP Relay | 1 |

## Missing Source Trace Risks

- One trace per object is enough for structural coverage but not enough for strong evidence coverage.
- Trace snippets are mock examples in Package 0 sample data.
- A trace supports a field; it does not guarantee legal, procurement, safety, or quality sufficiency.

## Known Limitations

- No crawler is implemented.
- No live source verification is performed.
- Source trace confidence is heuristic and sample-bound.

## Download Files

- `data/downloads/action_objects_v0_1.json`
- `data/downloads/source_traces_v0_1.json`
- `data/downloads/objective_scores_v0_1.json`
- `data/downloads/golden_queries_v0_1.json`
