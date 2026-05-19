# Hugging Face Demo

## Manual Space Setup

1. Create a new Hugging Face Space manually.
2. Choose Gradio as the SDK.
3. Upload files from `hf_demo/`.
4. Upload or vendor the `src/ai_objective_index` package if needed by the Space build.
5. Run the Space.

Do not include tokens in the repository.

## Local Run

```bash
pip install -r hf_demo/requirements.txt
python hf_demo/app.py
```

If Gradio is missing, the app prints:

```text
Install gradio to run the Hugging Face demo locally.
```

## Data Scope

The demo exposes a `data_scope` dropdown:

- `sample`: default sample records
- `generated`: local fixture extraction records
- `integrated`: sample + generated records
- `curated`: manually curated candidates
- `public_beta`: curated candidates that pass the evidence gate
- `mcp_registry`: local Official MCP Registry intake records
- `public_beta_mcp`: registry records that pass the registry evidence gate

For non-Gradio use, call:

```python
run_demo_query("cheap image generation API", data_scope="integrated")
run_demo_query("cheap image generation API", data_scope="public_beta")
run_demo_query("browser automation MCP", data_scope="mcp_registry")
run_demo_query("browser automation MCP", data_scope="public_beta_mcp")
```

Generated, curated, and registry records remain `EXTRACTED_UNVERIFIED`. If `public_beta` or `public_beta_mcp` has no ready objects, the demo shows a warning instead of falling back to fake sample data. When `public_beta_mcp` has rows, the demo displays them as registry metadata candidates, not verified servers. No live crawling, registry live mode, or network fetch is performed by the demo.

For the v0.2 real-data public beta pack, `public_beta_mcp` may contain Official MCP Registry metadata candidates. The demo must continue to label them as not verified, not security certified, not quality guaranteed, and not action-ready.

## Dataset Repo Setup

1. Create a Hugging Face Dataset repository manually.
2. Upload files from `hf_dataset/`.
3. Use `hf_dataset/README.md` as the dataset card draft.

## Do Not Automate Publish

This repository does not publish to Hugging Face automatically. It does not require Hugging Face tokens or external credentials.

Package 7B may create release-candidate files that reference the demo. It still does not create a Space, upload files, or use tokens.

Package 8B adds manual upload guides under `launch/manual_public_beta_v0_2/`. They are instructions only and do not upload files.

Package 8D leaves Hugging Face publishing on HOLD. The GitHub staging repository may be linked, but HF Space and Dataset links must remain TODO/HOLD until the user manually creates them. No HF token should be stored in the repository.

## Package 8F Manual Upload Bundle

Package 8F creates self-contained folders for manual Hugging Face upload:

```bash
python -m ai_objective_index.hf_upload_packager
python -m ai_objective_index.hf_upload_audit
```

Upload `hf_upload/space/` to a Gradio Space and `hf_upload/dataset/` to a Dataset through the Hugging Face web UI. Start both as private. Do not add tokens or secrets.

The Space defaults to `public_beta_mcp` when local registry metadata candidates are bundled. Those candidates are not verified, not security certified, not a quality guarantee, not purchasing advice, and not action-ready.

## Package 8G Private Upload Assist

Package 8G can check local Hugging Face authentication and upload the already-generated `hf_upload/space/` and `hf_upload/dataset/` bundles to private Hugging Face repos:

```bash
python -m ai_objective_index.hf_auth_check
python -m ai_objective_index.hf_private_upload --dry-run
python -m ai_objective_index.hf_private_upload --execute
python -m ai_objective_index.hf_post_upload_qa
```

Targets are `edict-lab/ai-objective-index-demo` for the Gradio Space and `edict-lab/ai-objective-index-sample` for the Dataset. Package 8G does not request tokens in chat, print tokens, store tokens, make repos public, or post launch announcements. If local CLI/API authentication is missing, use `huggingface_upload/HF_UPLOAD_COMMANDS.md` or `huggingface_upload/HF_BROWSER_FALLBACK_STEPS.md`.

Current private deployment links:

- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- GitHub private repo: https://github.com/Isometric-Architect/ai-objective-index

These are private review links unless the owner manually changes visibility. They are not a public release claim.

## Read-Only Boundary

The demo and dataset are read-only. They do not crawl, buy, book, pay, log in, send email, submit forms, modify accounts, claim suppliers, verify suppliers, or sign contracts.
