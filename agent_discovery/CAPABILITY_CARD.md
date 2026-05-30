# AOI Capability Card

AOI helps AI agents find source-traced capability/tool/API/MCP candidates for an objective, then preflight those candidates before use.

Package: `ai-objective-index`  
Version: `0.3.0a2`  
MCP name: `io.github.Isometric-Architect/ai-objective-index`  
Type: `objective_to_capability_discovery_and_preuse_trust_router`

## Best For

- finding source-traced MCP/tool/API candidates for a specific objective
- returning useful top candidates with missing fields
- adding conservative pre-use route decisions
- explaining HOLD/BLOCK reasons
- producing must-not-claim boundaries
- escalating to ResidualOps gates when enterprise use is needed

## Not For

- security certification
- provider verification
- automatic tool execution
- purchase recommendation
- legal/compliance/privacy/license clearance
- production readiness proof
- external action authorization

## Modes

- `discover`: return useful source-traced candidates, missing fields, preliminary route decisions, and next actions.
- `preflight`: separate tool availability from use authorization before an agent recommends or executes anything.

## Claim Boundary

- `candidate != verified`
- `metadata != proof`
- `tool_available != tool_authorized`
- `source_trace != security_certification`
- `route_decision != action_authorization`

Private ranking weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, commercial routing policy, real feedback memory, and customer-specific data remain private and are not included in this card.
