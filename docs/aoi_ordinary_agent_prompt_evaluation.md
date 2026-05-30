# AOI Ordinary Agent Prompt Evaluation

Ordinary AI agents can fail in predictable ways: they may hallucinate candidates, over-recommend, skip HOLD, treat metadata as proof, or confuse tool availability with authorization.

AOI Agent Discovery 3 creates deterministic offline fixtures that compare a naive tool-recommendation answer with an AOI-guided answer. The AOI-guided path is discover-first and preflight-second:

1. return useful candidates even when all are HOLD;
2. show source traces and missing fields;
3. attach route decisions and next actions;
4. include must-not-claim boundaries;
5. route tool, code, and data risks to ResidualOps paths.

The fixture is not a live LLM benchmark and does not prove universal agent behavior. It is a local evaluation pack for improving prompt design and product surface clarity.

AOI Agent Discovery 4 adds manual cross-model feedback intake on top of this fixture. The next evaluation focus is whether a Capability Decision Packet and granular route semantics make ordinary agents less likely to confuse discovered, trusted, authorized, and executable states.
