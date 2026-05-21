# Public / Private Split

| Public | Private |
| --- | --- |
| Schemas | Exact operational weights |
| API/MCP endpoint shapes | Scoring thresholds |
| High-level score components | Anti-gaming heuristics |
| Source-trace methodology | Provider trust priors |
| ALLOW/HOLD/BLOCK labels | Private negative controls |
| Limitations and claim boundaries | Private probe seeds |
| Sample/public beta data | Receipt weighting logic |
| Demo profile names such as `demo_profile_v0_1` | Commercial/enterprise routing policy |

The public project can show how route decisions are represented and audited. It should not expose the private kernel values that would make clone-and-game behavior easier.

Private inventories should live outside committed public files, preferably under ignored local paths such as `.aoi_private/`, `private_kernel/`, or `private_calibration/`.
