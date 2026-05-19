# Token Revocation At Public Stage

After public visibility is complete, revoke temporary Hugging Face upload tokens if no further upload is needed.

Manual steps:

1. Open Hugging Face Settings.
2. Open Access Tokens.
3. Delete/Revoke `aoi-private-upload`.
4. Do not paste tokens into chat.
5. Do not commit tokens.
6. If later updates are needed, create a new temporary token and keep it local.

Token revocation does not remove the already uploaded Space or Dataset.

