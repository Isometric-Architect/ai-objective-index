# Hugging Face CLI Upload Commands

If CLI authentication is needed, run these locally in PowerShell:

```powershell
python -m pip install huggingface_hub
hf auth login
# or
huggingface-cli login
```

Then run:

```powershell
python -m ai_objective_index.hf_private_upload --execute
```

Do not paste Hugging Face tokens into ChatGPT/Codex chat. Do not save tokens in the repository. Do not commit tokens.
