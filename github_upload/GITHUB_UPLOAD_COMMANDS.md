# GitHub Upload Commands

These commands are manual fallback instructions. Do not paste tokens into this file.

```powershell
git init
git branch -M main
git add .
git commit -m "Initial AI Objective Index public beta candidate"
gh auth login
gh repo create Isometric-Architect/ai-objective-index --private --source=. --remote=origin --push
```

If the remote repository already exists, do not force push. Verify the remote URL first:

```powershell
git remote -v
git push -u origin main
```
