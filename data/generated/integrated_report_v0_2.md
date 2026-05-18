# Integrated Generated Extraction Report v0.2

## What Package 6C Integrates

Package 6C integrates Package 6A generated fixture extraction outputs into explicit local AOI helper flows. Generated records can be searched, scored, compared, explained, and evaluated when callers choose `generated` or `integrated` scope.

## Scope

- Data scope: `integrated`
- Object count: `23`
- Trace count: `46`
- Generated EXTRACTED_UNVERIFIED object count: `3`

## Data Sources

- sample seed data from Package 0/1
- generated fixture extraction data from Package 6A

## Status Labels

Status counts: `{'active': 19, 'beta': 1, 'EXTRACTED_UNVERIFIED': 3}`

Generated fixture records remain `EXTRACTED_UNVERIFIED`. They are not verified supplier claims.

## EXTRACTED_UNVERIFIED Warning

`EXTRACTED_UNVERIFIED` means a record was produced by local fixture extraction and source-trace mapping. It does not mean the supplier verified the claim, and it does not mean the data is complete, current, or safe for production decisions.

## Top Example Results

| object_id | name | status | score | missing |
| --- | --- | --- | --- | --- |
| image_api_fixture | PixelForge API | EXTRACTED_UNVERIFIED | 69.12 | 1 |
| aoi-codepilot-studio | CodePilot Studio | active | 56.0 | 2 |
| ocr_api_fixture | ClearRead OCR API | EXTRACTED_UNVERIFIED | 55.34 | 2 |
| aoi-clearscan-ocr-api | ClearScan OCR API | active | 53.5 | 1 |
| aoi-modelbridge-gateway | ModelBridge Gateway | active | 53.5 | 1 |
| aoi-flowpilot-automations | FlowPilot Automations | active | 53.5 | 2 |
| aoi-findwise-search-api | Findwise Search API | active | 53.5 | 2 |
| aoi-signallens-monitor | SignalLens Monitor | active | 53.5 | 2 |
| aoi-searchmcp-relay | SearchMCP Relay | active | 51.96 | 2 |
| aoi-vectornest-db | VectorNest DB | active | 48.5 | 1 |

## Missing Fields Summary

- Total missing-field signals: `47`
- Objects with missing fields: `23`
- Most common missing fields: `{'refund_policy': 22, 'api_reference_url': 3, 'privacy_policy': 2, 'data_retention_policy': 2, 'enterprise_sla': 1, 'model_training_opt_out_scope': 1, 'ranking_source_partners': 1, 'security_policy_url': 1, 'voice_consent_audit_details': 1, 'connector_data_subprocessor_list': 1, 'hosted_pool_security_review': 1, 'model_accuracy_by_document_type': 1, 'commercial_rights_edge_cases': 1, 'source_index_scope': 1, 'model_license_matrix': 1, 'supported_model_provider_matrix': 1, 'maintainer_security_contact': 1, 'workforce_location_details': 1, 'pii_redaction_default_behavior': 1, 'commercial_use_terms': 1, 'docs_url': 1, 'api_access': 1}`

## Integrated Eval Summary

- Query count: `4`
- Result count: `20`
- Average score: `55.66`
- Source trace coverage: `1.0`
- Top result names: `['PixelForge API', 'BrowserPilot MCP', 'ClearRead OCR API', 'PixelForge API']`

## Package 6D DataScope QA

- Default data scope: `sample`
- Sample objects: `20`
- Generated objects: `3`
- Integrated objects: `23`
- Generated status discipline: `EXTRACTED_UNVERIFIED`
- Live network used: `False`
- Beta readiness token: `PASS`

Package 6D adds local beta-readiness checks. This is Productization Mode work: implementation may proceed, but public product claims require product evidence.

## Limitations

- No live crawling.
- No network fetch.
- No external LLM extraction.
- Generated fixture records are local test artifacts.
- Source traces support fields but do not guarantee correctness or currentness.
- Objective scores are fit heuristics, not quality guarantees.

## Not Implemented

- live crawling
- supplier verification
- Hugging Face publishing
- community posting
- payment, booking, login, email sending, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification
