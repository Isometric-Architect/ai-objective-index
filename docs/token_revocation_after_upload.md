# Token Revocation After Upload

After Hugging Face upload work is done, consider revoking temporary upload tokens.

Steps:

1. Do not paste tokens into chat.
2. Do not commit tokens.
3. Open Hugging Face Settings.
4. Open Access Tokens.
5. Find `aoi-private-upload`.
6. Delete/Revoke the token if no further upload is needed.

If a public visibility switch still needs Hugging Face API access, revoke the token after the switch. Already-uploaded Space and Dataset repos remain uploaded after token revocation.
