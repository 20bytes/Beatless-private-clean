# Beatless Codex-Primary Architecture

Status: active target architecture after the Claude Code primary-executor cutover.

## Runtime Split

Beatless keeps Hermes as the 24/7 control plane and uses Codex as the default
heavy executor.

```text
Hermes gateway / cron
  -> Python wake-gate scripts
  -> Codex CLI (`codex exec`)
  -> GitHub / Zotero / Obsidian / blog / research workspaces
```

Claude Code is now only a manual legacy fallback. Wake-gate scripts should not
spawn `claude -p` or depend on Claude slash commands.

## Active Wake-Gate Execution

| Wake-gate | Trigger | Primary executor | Embedded spec |
| --- | --- | --- | --- |
| `github-response.py` | Open PR comments, unreplied feedback, failing CI | Codex | `pipelines/pr-followup.md` |
| `github-pr.py` | Claimable GitHub issues that pass preflight | Codex | `pipelines/github-pr.md` + `skills/pr-direction-check/SKILL.md` |
| `auto-research.py` | Research workspace outputs/progress | Codex | `commands/exp/exp-run.md` |
| `blog-maintenance.py` | Blog audit tick | none; audit-only | writes status/audit files |

## Codex Policy

The shared executor wrapper lives at `hermes-scripts/beatless_executor.py`.

Default settings come from `.env.local` or `~/.hermes/.env`:

```bash
BEATLESS_PRIMARY_EXECUTOR=codex
CODEX_BIN=codex
BEATLESS_CODEX_HOME=~/.codex
BEATLESS_CODEX_MODEL=gpt-5.5
BEATLESS_CODEX_REASONING_EFFORT=xhigh
BEATLESS_CODEX_SANDBOX=workspace-write
CODEX_TIMEOUT_SECONDS=7200
BEATLESS_ALLOW_CLAUDE_FALLBACK=1
```

Every wake-gate uses:

```bash
codex -m "$BEATLESS_CODEX_MODEL" \
  -c "model_reasoning_effort=\"$BEATLESS_CODEX_REASONING_EFFORT\"" \
  --ask-for-approval never \
  --sandbox "$BEATLESS_CODEX_SANDBOX" \
  exec --skip-git-repo-check --ephemeral -C <workspace> -
```

The prompt is passed over stdin, with the relevant Beatless pipeline spec
embedded directly. This removes the old dependency on Claude Code slash-command
resolution.

## Model Roles

| Role | Runtime |
| --- | --- |
| Lacia | Hermes orchestration and memory |
| Methode | Hermes routing; Codex executes implementation |
| Satonus | Codex review gate |
| Snowdrop | Codex research execution with Gemini optional |
| Kouka | Hermes/MiniMax delivery and media tasks |

Gemini remains the second-opinion/literature CLI. MiniMax remains for media and
delivery. Codex owns code, PR, review, and experiment execution.
