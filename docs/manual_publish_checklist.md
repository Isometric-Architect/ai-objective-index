# Manual Publish Checklist

Package 7B does not publish automatically. Use this checklist if a human decides to publish a public beta.

1. Review `README.md`.
2. Run `python -m pytest`.
3. Run `python -m ai_objective_index.mcp_smoke`.
4. Run `python -m ai_objective_index.datascope_qa`.
5. Run `python -m ai_objective_index.beta_readiness`.
6. Run `python -m ai_objective_index.release_readiness`.
7. Run `python -m ai_objective_index.release_claim_audit`.
8. Run `python -m ai_objective_index.public_beta_packager`.
9. Run `python -m ai_objective_index.smoke_all`.
10. Run `python -m ai_objective_index.curated_index_export`.
11. Run `python -m ai_objective_index.curated_eval`.
12. Run `python -m ai_objective_index.curated_report_generator`.
13. Run `python -m ai_objective_index.registry_intake.mcp_registry_export --use-fixture`.
14. Run `python -m ai_objective_index.registry_intake.mcp_registry_eval`.
15. Run `python -m ai_objective_index.registry_intake.mcp_registry_report_generator`.
16. Run `python -m ai_objective_index.registry_intake.live_registry_run` or use the manual raw fallback.
17. If explicitly approved, run `python -m ai_objective_index.registry_intake.live_registry_run --allow-network --max-servers 50`.
18. Run `python -m ai_objective_index.registry_intake.registry_beta_dataset_builder`.
19. Run `python -m ai_objective_index.registry_intake.registry_quality_audit`.
20. Run `python -m ai_objective_index.registry_intake.registry_beta_report_generator`.
21. Run `python -m ai_objective_index.registry_intake.real_payload_activation --use-existing-raw`.
22. Run `python -m ai_objective_index.registry_intake.registry_payload_audit`.
23. Run `python -m ai_objective_index.registry_intake.registry_reprocess_all`.
24. Ensure `registry_payload_audit` says `real_payload_available=true`.
25. Ensure `fixture_leak_detected=false`.
26. If claiming MCP public beta data, ensure `public_beta_mcp_count > 0`.
27. Review curated validation results and ensure no placeholder objects appear in `public_beta`.
28. Review registry validation results and verify `public_beta_mcp` count.
29. Confirm `public_beta_mcp` says not verified and not security certified.
30. Run `python -m ai_objective_index.release_readiness`.
31. Run `python -m ai_objective_index.release_claim_audit`.
32. Confirm no security certification or supplier verification claims are made.
33. Run `python -m ai_objective_index.realdata_claim_audit`.
34. Run `python -m ai_objective_index.release_candidate_matrix`.
35. Run `python -m ai_objective_index.final_preflight`.
36. Run `python -m ai_objective_index.public_beta_realdata_packager`.
37. Run `python -m ai_objective_index.smoke_all`.
38. Run `python -m ai_objective_index.manual_launch_packager`.
39. Run `python -m ai_objective_index.launch_dry_run`.
40. Run `python -m ai_objective_index.no_secrets_audit`.
41. Run `python -m ai_objective_index.launch_claim_guard`.
42. Run `python -m ai_objective_index.release_archive_builder`.
43. Run `python -m ai_objective_index.github_staging` if GitHub staging upload is desired.
44. Review `github_upload/`.
45. Run `python -m ai_objective_index.github_post_upload_qa`.
46. Run `python -m ai_objective_index.github_link_binder`.
47. Run `python -m ai_objective_index.public_switch_preflight`.
48. Review `github_upload/GITHUB_WEB_REVIEW_CHECKLIST.md`.
49. Review `github_upload/PUBLIC_VISIBILITY_DECISION_CHECKLIST.md`.
50. Review `release/public_beta_v0_1/`, `release/public_beta_v0_2/`, and `launch/manual_public_beta_v0_2/`.
51. Create a GitHub release manually if desired.
52. Run `python -m ai_objective_index.hf_upload_packager` if Hugging Face upload prep is desired.
53. Run `python -m ai_objective_index.hf_upload_audit`.
54. Run `python -m ai_objective_index.hf_auth_check`.
55. Run `python -m ai_objective_index.hf_private_upload --dry-run`.
56. If local Hugging Face authentication is present and private upload is desired, run `python -m ai_objective_index.hf_private_upload --execute`.
57. Run `python -m ai_objective_index.hf_post_upload_qa`.
58. Run `python -m ai_objective_index.deployment_link_sync`.
59. Run `python -m ai_objective_index.private_deployment_qa`.
60. Run `python -m ai_objective_index.hf_github_crosslink_audit`.
61. Run `python -m ai_objective_index.deployment_push_sync --dry-run`.
62. If all private deployment checks pass, run `python -m ai_objective_index.deployment_push_sync --execute`.
63. Run `python -m ai_objective_index.public_launch_gate`.
64. Run `python -m ai_objective_index.public_visibility_switch --dry-run`.
65. Run `python -m ai_objective_index.public_launch_claim_audit`.
66. Run `python -m ai_objective_index.private_reviewer_packager`.
67. Run `python -m ai_objective_index.token_revocation_checklist`.
68. If no private reviewers are available, run `python -m ai_objective_index.ai_reviewer_simulation`.
69. Run `python -m ai_objective_index.issue_feedback_loop_packager`.
70. Run `python -m ai_objective_index.public_beta_message_guard`.
71. Run `python -m ai_objective_index.no_contact_launch_gate`.
72. Review `public_launch/NO_CONTACT_GO_NO_GO_DECISION.md`.
73. Run `python -m ai_objective_index.prepublic_sync --dry-run`.
74. Run `python -m ai_objective_index.final_public_dry_run`.
75. Run `python -m ai_objective_index.prepublic_state_report`.
76. If private sync is desired and dry-run is clean, run `python -m ai_objective_index.prepublic_sync --execute`.
77. Review `public_launch/FINAL_PUBLIC_SWITCH_INSTRUCTIONS.md`.
78. Review `public_launch/PREPUBLIC_REVIEW_CHECKLIST.md`.
79. Run `python -m ai_objective_index.public_launch_execute --dry-run`.
80. If the owner explicitly approves public switch, set `$env:AOI_PUBLIC_LAUNCH_CONFIRM="YES"` and run `python -m ai_objective_index.public_launch_execute --execute`.
81. Run `python -m ai_objective_index.public_url_qa`.
82. Run `python -m ai_objective_index.post_public_state_report`.
83. Review `public_launch/POST_PUBLIC_REVIEW_CHECKLIST.md`.
84. Run `python -m ai_objective_index.post_public_stabilization`.
85. Run `python -m ai_objective_index.public_issue_loop`.
86. Run `python -m ai_objective_index.token_revocation_verify`.
87. Run `python -m ai_objective_index.public_observation_plan`.
88. Run `python -m ai_objective_index.public_ops_baseline`.
89. Run `python -m ai_objective_index.worktree_hygiene_audit`.
90. Run `python -m ai_objective_index.github_issue_labels --dry-run`.
91. Run `python -m ai_objective_index.observation_log`.
92. Run `python -m ai_objective_index.release_next_decision_gate`.
93. Observe for 72 hours before broad community posting.
94. If CLI/API upload is unavailable, create a Hugging Face Space manually if desired and upload `hf_upload/space/`.
95. If CLI/API upload is unavailable, create a Hugging Face Dataset manually if desired and upload `hf_upload/dataset/`.
96. Submit to MCP Registry manually if desired.
97. Post a community feedback request manually if desired, after Package 8M/8N or equivalent review.

Do not claim AOI is an official standard, universally adopted, a quality guarantee, legal/security/compliance certification, purchasing advice, or an external action executor.

For v0.2 real-data public beta, also do not claim verified MCP servers, safe MCP servers, security certification, or quality guaranteed tools.

## Public Deployment Links

- GitHub repository: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample

## Package 8O Wave 1

96. Run `python -m ai_objective_index.github_release_manager --dry-run`.
97. Run `python -m ai_objective_index.community_launch_manager --dry-run`.
98. Run `python -m ai_objective_index.mcp_registry_server_json_builder`.
99. Run `python -m ai_objective_index.mcp_registry_submission_gate --dry-run`.
100. Run `python -m ai_objective_index.launch_wave1_report`.
101. If the release dry-run passes, run `python -m ai_objective_index.github_release_manager --execute`.
102. Do not submit MCP Registry unless eligibility is `PASS_SUBMIT_READY` and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set.

## Package 8P PyPI / Registry Readiness

103. Run `python -m ai_objective_index.package_metadata_audit`.
104. Run `python -m ai_objective_index.pypi_publish_readiness`.
105. Run `python -m ai_objective_index.mcp_registry_pypi_builder`.
106. Run `python -m ai_objective_index.mcp_registry_publish_readiness`.
107. Run `python -m ai_objective_index.pypi_upload_instructions`.
108. Run `python -m ai_objective_index.community_manual_queue`.
109. Do not upload to PyPI/TestPyPI in Package 8P.
110. Do not submit to MCP Registry until PyPI upload and registry readiness both pass.

## Package 8Q-A Local Build Readiness

111. Run `python -m ai_objective_index.local_build_tools --check`.
112. If needed, run `python -m ai_objective_index.local_build_tools --install`.
113. Run `python -m ai_objective_index.dist_build_runner`.
114. Run `python -m ai_objective_index.local_install_smoke`.
115. Run `python -m ai_objective_index.pypi_readiness_refresh`.
116. Do not paste PyPI/TestPyPI tokens into chat.
117. Do not upload to TestPyPI/PyPI until a later explicit upload package.

## Package 9A vNext Alignment

118. Run `python -m ai_objective_index.vnext_claim_audit`.
119. Confirm PyPI upload remains paused.
120. Confirm MCP Registry submission remains paused.
121. Review `docs/vnext/aoi_vnext_strategy.md`.
122. Do not claim AOI is already a security gateway, verified capability system, security certification, quality guarantee, official standard, or purchasing advice.
- MCP Registry submission: HOLD, manual only.

## Package 9F vNext Distribution Gate

123. Run `python -m ai_objective_index.vnext_surface_sync_audit`.
124. Run `python -m ai_objective_index.vnext_package_version_audit`.
125. Run `python -m ai_objective_index.residualops_alignment_audit`.
126. Run `python -m ai_objective_index.vnext_distribution_gate`.
127. Run `python -m ai_objective_index.vnext_pypi_resume_gate`.
128. Choose a vNext package version, likely `0.3.0` or `0.3.0a1`, before any upload-oriented package.
129. Resume 8Q-A only for local build/twine checks. Do not upload to PyPI/TestPyPI in 9F.

## Package 8Q-A Resumed vNext Build Candidate

130. Run `python -m ai_objective_index.version_apply_gate --dry-run`.
131. Run `python -m ai_objective_index.version_apply_gate --apply 0.3.0a1`.
132. Run `python -m ai_objective_index.local_build_tools --check`.
133. Run `python -m ai_objective_index.dist_build_runner`.
134. Run `python -m ai_objective_index.local_install_smoke`.
135. Run `python -m ai_objective_index.pypi_readiness_refresh`.
136. Run `python -m ai_objective_index.mcp_registry_readiness_refresh`.
137. Do not upload to TestPyPI/PyPI in this package.

## Package 8Q-C-alt Real PyPI Direct Upload

138. Run `python -m ai_objective_index.real_pypi_upload_gate`.
139. Run `python -m ai_objective_index.real_pypi_upload_runner --dry-run`.
140. If and only if the gate passes, set `$env:AOI_REAL_PYPI_UPLOAD_CONFIRM="YES"`.
141. Run `python -m ai_objective_index.real_pypi_upload_runner --execute`.
142. Enter username `__token__` and the real PyPI API token only into the local twine prompt.
143. Run `python -m ai_objective_index.real_pypi_install_verify`.
144. Run `python -m ai_objective_index.real_pypi_release_audit`.
145. Run `python -m ai_objective_index.mcp_registry_after_pypi_gate`.
146. Do not submit MCP Registry metadata in Package 8Q-C-alt.
147. Do not paste tokens into chat, create `.pypirc`, post to communities, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## AOI 0.3.0a2 PyPI Marker Sync and MCP Registry Recovery

147a. Confirm README contains `mcp-name: io.github.Isometric-Architect/ai-objective-index`.
147b. Confirm `pyproject.toml`, `src/ai_objective_index/__init__.py`, and `.mcp/server.json` all use `0.3.0a2`.
147c. Run `python -m ai_objective_index.aoi_030a2_marker_sync`.
147d. Run `python -m ai_objective_index.aoi_030a2_build_verify`.
147e. Run `python -m ai_objective_index.aoi_030a2_pypi_upload_gate`.
147f. Only if the upload gate is otherwise ready, set `$env:AOI_REAL_PYPI_UPLOAD_CONFIRM="YES"` and run the upload through the interactive twine prompt. Do not pass tokens in command-line flags or files.
147g. Run `python -m ai_objective_index.aoi_030a2_pypi_verify`.
147h. Run `python -m ai_objective_index.aoi_mcp_registry_recovery_gate`.
147i. Only if the recovery gate is PASS, set `$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"` and run the guarded registry publish helper locally.
147j. Do not overwrite or yank 0.3.0a1, commit `.pypirc`, commit `mcp-publisher`, post to communities, claim certification, claim correctness proof, claim product readiness, or authorize external actions.

## Package 8R MCP Registry Publish Gate

148. Run `python -m ai_objective_index.mcp_publisher_setup --check`.
149. Run `python -m ai_objective_index.mcp_registry_manifest_final_audit`.
150. Run `python -m ai_objective_index.mcp_registry_publish_runner --dry-run`.
151. If `mcp-publisher` is missing, install it from the official modelcontextprotocol/registry release source and rerun the setup check.
152. Run `python -m ai_objective_index.mcp_registry_publish_runner --login` only after `mcp-publisher` is available.
153. Do not run `--execute` unless the manifest audit passes, GitHub auth works, and `$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"` is set.
154. After any publish attempt, run `python -m ai_objective_index.mcp_registry_post_publish_verify`.
155. Run `python -m ai_objective_index.mcp_registry_release_audit`.
156. Registry publication is not verification, security certification, quality guarantee, product readiness, purchasing advice, or action authorization.

## Package 8S Technology Protection

157. Run `python -m ai_objective_index.tech_protection_audit`.
158. Run `python -m ai_objective_index.public_private_split_audit`.
159. Run `python -m ai_objective_index.package_artifact_exposure_audit`.
160. Run `python -m ai_objective_index.anti_clone_risk_audit`.
161. Run `python -m ai_objective_index.license_ip_positioning_audit`.
162. Run `python -m ai_objective_index.private_kernel_template_generator`.
163. Run `python -m ai_objective_index.mcp_registry_pre_publish_protection_gate`.
164. Do not expose exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, commercial routing policy, or private data strategy.
165. Do not submit MCP Registry metadata until the protection gate is PASS or an explicit remediation decision is made.

## Package 8R-B MCP Registry Submit

166. Run `python -m ai_objective_index.mcp_publisher_installer --check`.
167. If missing, run `python -m ai_objective_index.mcp_publisher_installer --instructions`.
168. Run `python -m ai_objective_index.mcp_publisher_auth_check --login` only after publisher availability is confirmed.
169. Run `python -m ai_objective_index.mcp_registry_publish_preflight`.
170. Run `python -m ai_objective_index.mcp_registry_submit_execute --dry-run`.
171. Do not run execute unless preflight is PASS and `$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"` is set.
172. After execute or manual publish, run `python -m ai_objective_index.mcp_registry_submit_reconcile`.
173. Run `python -m ai_objective_index.mcp_registry_discovery_report`.
174. Do not paste GitHub tokens into chat or commit credentials.

These links are public after Package 8K. The GitHub prerelease and real PyPI package exist; community posting and MCP Registry submission remain gated/HOLD. `public_beta_mcp` records are source-traced registry metadata candidates; they are not verified, not safe/certified, not security certified, not a quality guarantee, and not purchasing advice.
