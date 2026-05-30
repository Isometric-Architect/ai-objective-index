# Ordinary Agent Failure Modes

Ordinary agents may hallucinate candidates, over-recommend, skip HOLD, confuse tool availability with tool authorization, treat metadata as proof, treat README claims as verification, treat a registry listing as approval, or execute before policy checks.

AOI counters this by making discovery useful first, then requiring preflight before use. Discover mode keeps HOLD candidates visible with next actions. Preflight mode blocks external actions and overclaims. ResidualOps routes enterprise review to AgentSec, QIRA, DataCapsule, or the dashboard/share-pack layer.
