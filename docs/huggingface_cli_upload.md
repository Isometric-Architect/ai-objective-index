# Hugging Face CLI Upload

AOI supports a private Hugging Face upload helper for users who already have local Hugging Face CLI/API authentication.

## Authentication

Use one of these locally:

```powershell
hf auth login
```

or:

```powershell
huggingface-cli login
```

Do not paste tokens into ChatGPT/Codex chat. Do not save tokens in the repository. Do not commit tokens.

## Upload

Run a dry run first:

```powershell
python -m ai_objective_index.hf_private_upload --dry-run
```

Then, only if authenticated:

```powershell
python -m ai_objective_index.hf_private_upload --execute
```

The helper keeps Space and Dataset private and does not change public visibility.

