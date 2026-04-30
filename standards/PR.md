# PR Workflow Standard — Seven-Step Method

A structured, machine-parseable standard for submitting Pull Requests via the Fork-based open source contribution workflow. Follow each step sequentially.

---

## Core Rule

> **Never work directly on `main`.** Every change lives on a dedicated branch — isolated, reviewable, and revertible.

---

## Step 1: Fork

Copy the upstream repository to your own GitHub account. Click **Fork** on the upstream repo page. Required when you lack write access; team repos with write access may branch directly.

## Step 2: Clone

```bash
git clone https://github.com/<you>/<repo>.git && cd <repo>
git remote add upstream https://github.com/<owner>/<repo>.git
```

- `origin` = your fork (push target), `upstream` = original repo (sync source)

## Step 3: Branch

Sync first, then create a dedicated branch.

```bash
git checkout main && git pull upstream main
git checkout -b <type>-<short-description>
```

- Descriptive names: `fix-empty-array-geval`, `docs-update-pr-guide`, `feat-user-profile`
- Forbidden: `test`, `new-branch`, `update`, `temp` — too vague

## Step 4: Commit

```bash
git add <specific-files>
git commit -m "<type>: <concise description>"
```

- Start with a verb: `fix`, `add`, `refactor`, `docs`
- Be specific: `fix: handle empty array in geval` (good) vs `fix bug` (bad)
- One logical change per commit — atomic and bisect-friendly

## Step 5: Push

```bash
git push -u origin <branch-name>
```

- Always verify push target: `git remote get-url origin` must be your fork, never upstream

## Step 6: Open PR

**Pre-submission checks:** base = upstream `main`, head = your fork branch, title matches commit convention.

**PR description template (required):**

```markdown
## What changed
- <list of changes with file references>

## Why
- <root cause or motivation — show you understand the codebase>

## How to verify
- <exact test commands and expected output>

## Impact scope
- <which modules are affected, what is NOT affected>
```

- Link issues: `Fixes #<number>` (auto-closes on merge)
- Attach screenshots for UI changes
- Keep tone humble and factual

## Step 7: Review and Iterate

PR submission starts the conversation, not ends it. Push fixes to the same branch — the PR updates automatically. No need to open a new PR.

```bash
git add <files>
git commit -m "refactor: address review feedback"
git push origin <branch-name>
```

---

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Working on `main` | Tangled history, sync conflicts | Always branch first |
| Oversized PR | Hard to review, slow to merge | One logical change per PR, <100 lines preferred |
| Empty description | Reviewer cannot assess intent or impact | Use the 4-section template above |
| Generic AI phrases | Signals low-effort contribution | Write specific, factual descriptions |
| Pushing to upstream | Rejected or damages the repo | Verify `origin` points to your fork |

---

## Quick-Reference Command Cheat Sheet

```bash
# 1. Clone fork + configure upstream
git clone https://github.com/<you>/<repo>.git && cd <repo>
git remote add upstream https://github.com/<owner>/<repo>.git

# 2. Sync and branch
git checkout main && git pull upstream main
git checkout -b fix-<issue-slug>

# 3. Develop and commit
git add <files>
git commit -m "fix: <description>"

# 4. Push to fork
git push -u origin fix-<issue-slug>

# 5. Create PR (CLI)
gh pr create --repo <owner>/<repo> \
  --title "fix: <description>" \
  --body "<use template above>"

# 6. Respond to review
git add <files> && git commit -m "refactor: address review feedback"
git push origin fix-<issue-slug>

# 7. Sync if upstream moved ahead
git fetch upstream && git rebase upstream/main
git push --force-with-lease origin fix-<issue-slug>
```
