# Contributing to TGPC Rx Registry

We follow a strict **Feature Branch Workflow** to ensure stability of the `main` branch.

## 🌲 Branching Strategy

**NEVER commit directly to `main` for experimental or complex changes.**

### 1. Create a Branch
Always start by creating a new branch for your task:
```bash
git checkout -b feature/name-of-feature
# or
git checkout -b fix/issue-description
```

### 2. Make Changes & Test Locally
Edit files and verify they work on your machine.
- Run `python -m tgpc update` to test backend logic.
- View `docs/index.html` to test frontend.

### 3. Commit Changes
```bash
git add .
git commit -m "feat: description of changes"
```

### 4. Push & Pull Request
Push your branch to GitHub:
```bash
git push -u origin feature/name-of-feature
```
Then, go to GitHub and open a **Pull Request (PR)** against `main`.

### 5. Merge
Once the PR is reviewed and checks pass (Workflows), merge it into `main`.

---

## 🛡 Protected Files
- `README.md` is **LOCKED**. Do not attempt to modify it without unlocking it first.
- The `lock-readme` workflow ensures this immutability on GitHub.
