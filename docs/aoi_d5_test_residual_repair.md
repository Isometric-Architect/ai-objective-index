# AOI D5 Test Residual Repair

D5 includes a narrow repair for the registry/datascope payload-state residual classified in D4.

The issue was generated payload nesting in `data/registry/mcp_registry_raw_v0_1.json`. Repeated local fixture/export flows produced many nested `payload` wrappers. `real_payload_guard.py` used recursive payload inspection and could hit recursion depth while deciding whether a fixture would overwrite preserved raw registry state.

The D5 repair is deliberately narrow:

- unwrap payload wrappers iteratively;
- keep a depth and cycle guard;
- avoid staging generated registry payload leftovers;
- add a regression test for deeply wrapped payloads;
- re-run the failing registry/datascope slice.

This repair does not fetch registry data, publish packages, certify security, prove correctness globally, or authorize actions.
