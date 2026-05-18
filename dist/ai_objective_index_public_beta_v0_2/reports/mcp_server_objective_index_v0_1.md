# MCP Server Objective Index v0.1

Date: 2026-05-13

This is a v0.1 benchmark report based on sample/extracted records. It is not a quality guarantee, official ranking, legal advice, purchasing advice, or safety certification.

## What This Report Is

This report summarizes the read-only AOI benchmark sample for objective-fit comparison, with emphasis on MCP/server-like objects where present.

## Dataset Scope

- Action objects: 20
- Source traces: 20
- Status counts: {'active': 19, 'beta': 1}

## Methodology

Records are loaded from Package 0 sample data, scored with the Package 1 objective-fit heuristic, and summarized without crawling or network calls.

## Scoring Formula Summary

The v0.1 score combines relevance, cost fit, policy clarity, documentation quality, trust signal, source trace coverage, freshness, capability fit, and structuredness, then subtracts missing-field, stale, unsafe-claim, and ambiguity penalties.

## Top Ranked Sample Objects

| object_id | name | object_type | objective_score | confidence |
| --- | --- | --- | --- | --- |
| aoi-codepilot-studio | CodePilot Studio | saas | 56.0 | 0.84 |
| aoi-clearscan-ocr-api | ClearScan OCR API | api | 53.5 | 0.88 |
| aoi-modelbridge-gateway | ModelBridge Gateway | gateway | 53.5 | 0.87 |
| aoi-flowpilot-automations | FlowPilot Automations | workflow_tool | 53.5 | 0.82 |
| aoi-findwise-search-api | Findwise Search API | api | 53.5 | 0.85 |
| aoi-signallens-monitor | SignalLens Monitor | monitoring_tool | 53.5 | 0.86 |
| aoi-searchmcp-relay | SearchMCP Relay | mcp_server | 51.96 | 0.82 |
| aoi-vectornest-db | VectorNest DB | database | 48.5 | 0.85 |
| aoi-embedlite-api | EmbedLite API | api | 48.5 | 0.89 |
| aoi-doculift-extraction-api | DocuLift Extraction API | api | 48.48 | 0.86 |

## MCP/Server-Related Objects

| object_id | name | object_type | capabilities |
| --- | --- | --- | --- |
| aoi-searchmcp-relay | SearchMCP Relay | mcp_server | mcp_server, web_search, source_snippets, result_filtering |
| aoi-browserpilot-mcp | BrowserPilot MCP | mcp_server | mcp_server, browser_automation, screenshots, dom_inspection |

## Source Trace Coverage

- Object-level trace coverage: 1.0
- Score distribution among displayed top objects: {'count': 10, 'min': 48.48, 'max': 56.0, 'average': 52.09, 'buckets': {'0-24': 0, '25-49': 3, '50-74': 7, '75-100': 0}}

## Missing Fields Summary

- Objects with missing fields: 20
- Total missing-field signals: 40
- Most common missing fields: {'refund_policy': 20, 'api_reference_url': 3, 'privacy_policy': 2, 'enterprise_sla': 1, 'model_training_opt_out_scope': 1, 'ranking_source_partners': 1, 'security_policy_url': 1, 'voice_consent_audit_details': 1, 'connector_data_subprocessor_list': 1, 'hosted_pool_security_review': 1, 'model_accuracy_by_document_type': 1, 'commercial_rights_edge_cases': 1, 'source_index_scope': 1, 'model_license_matrix': 1, 'supported_model_provider_matrix': 1, 'maintainer_security_contact': 1, 'workforce_location_details': 1, 'pii_redaction_default_behavior': 1}

## Known Limitations

- Sample records are fake but realistic.
- Source traces are mock traces and do not prove completeness or currentness.
- The report is read-only and does not execute external actions.

## Download Files

- `data/downloads/action_objects_v0_1.json`
- `data/downloads/source_traces_v0_1.json`
- `data/downloads/objective_scores_v0_1.json`
- `data/downloads/golden_queries_v0_1.json`

## Claim Boundary

This is a v0.1 benchmark report based on sample/extracted records. It is not a quality guarantee, official ranking, legal advice, purchasing advice, or safety certification.
