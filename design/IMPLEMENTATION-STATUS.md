# Constellation v3 — Implementation Status

> Date: 2026-04-22
> Status: Superseded by Codex-primary execution cutover. See `docs/CODEX_PRIMARY_ARCHITECTURE.md`.

## What's Been Done

### 1. Hermes Agent Configuration

**Config**: `~/.hermes/config.yaml`

```yaml
model:
  default: "kimi-k2.6"          # Orchestrator (Lacia)
  provider: "kimi-coding"       # Built-in provider, auto-detects <provider-key-prefix> prefix

providers:
  step:                         # Named custom provider for Step 3.5 Flash
    name: "Step 3.5 Flash"
    base_url: "https://api.stepfun.com/step_plan/v1"
    key_env: "STEPFUN_API_KEY"

delegation:                     # Subagents use Step for fast execution
  provider: "step"
  model: "step-3.5-flash"
  max_concurrent_children: 5
  max_spawn_depth: 2

cron:
  script_timeout_seconds: 7200  # 2h for long Codex jobs

model_aliases:                  # Quick model switching
  step:    { model: "step-3.5-flash", provider: step }
  minimax: { model: "MiniMax-M2.7",   provider: minimax }
  kimi:    { model: "kimi-k2.6",      provider: kimi-coding }
```

**Env**: `~/.hermes/.env` (copied from `~/claw/.env`, NOT symlinked)
- Fixed `KIMI_BASE_URL=https://api.kimi.com/coding` (no `/v1` suffix — Anthropic SDK appends it)
- All API keys: KIMI, MINIMAX, STEPFUN, OPENROUTER, GOOGLE, GH_TOKEN, etc.

**SOUL.md**: `~/.hermes/SOUL.md` — Beatless personality (Lacia/Methode/Kouka routing).

### 2. Three-Model Routing Verified

| Model | Command | Status |
|-------|---------|--------|
| Kimi K2.6 (default) | `hermes chat -q "..."` | Working |
| MiniMax M2.7 | `hermes chat -q "..." --model MiniMax-M2.7 --provider minimax` | Working |
| Step 3.5 Flash | `hermes chat -q "..." --model step` | Working |

### 3. Gateway & Heartbeat

- `hermes gateway install` — installed as systemd user service
- `hermes gateway start` — running, cron ticker active every 60s
- Linger enabled — survives SSH logout
- No messaging platforms configured yet (Telegram deferred)

### 4. Cron Jobs (4 Active)

| Job | Schedule | Script (wake-gate) | Execution |
|-----|----------|---------------------|-----------|
| GitHub Response | every 60m | `github-response.py` — checks open PRs with new activity | Script calls Codex with embedded `pipelines/pr-followup.md` |
| GitHub PR Pipeline | every 150m | `github-pr.py` — checks claimable issues | Script calls Codex with embedded `pipelines/github-pr.md` and direction-check spec |
| Auto Research | every 240m | `auto-research.py` — checks `~/research/**/outputs/` | Script calls Codex with embedded `commands/exp/exp-run.md` |
| Blog Maintenance | every 720m | `blog-maintenance.py` — audits blog dir | Audit-only; no heavy executor |

**How cron works** (Codex-routed jobs):
1. Gateway ticks every 60s, checks for due jobs
2. Wake-gate script runs (up to 7200s timeout via `cron.script_timeout_seconds`)
3. Script checks if work exists (< 30s)
4. If no work: prints `{"wakeAgent": false}` → job skipped, zero cost
5. If work found: script calls `codex exec` through `hermes-scripts/beatless_executor.py`
6. Codex runs autonomously (30min–2h), output captured by script
7. Script prints Codex output → Hermes agent wakes to summarize/remember
8. Hermes agent (Kimi, ~3 turns) saves key outcomes to MEMORY.md

**Key directories**:
- `~/workspace` — GitHub repos are forked/cloned here (PR pipeline, response)
- `~/research` — Experiment directories with `outputs/` subdirs

### 5. Wake-Gate Scripts

Location: `~/.hermes/scripts/`

All scripts follow the same pattern:
- Quick check if work exists (< 30s)
- If no work: `{"wakeAgent": false}` → zero token cost
- If work found: call Codex through `beatless_executor.run_codex_exec`
- Capture output, print for Hermes delivery

| Script | Check Logic | Codex Embedded Spec | CWD |
|--------|-------------|-------------------|-----|
| `github-response.py` | `gh search prs --author=<your-github-user>` + activity marker | `pipelines/pr-followup.md` | `~/workspace` |
| `github-pr.py` | `gh search issues --label=good first issue,help wanted,bug` | `pipelines/github-pr.md` | `~/workspace` |
| `auto-research.py` | Glob `~/research/**/outputs/*/` + freshness marker | `commands/exp/exp-run.md` | experiment dir |
| `blog-maintenance.py` | Check `~/claw/blog/` exists | none; audit-only | — |

---

## Architecture: How the Pieces Fit

```
┌─────────────────────────────────────────────────────────────┐
│                  HERMES GATEWAY (systemd)                    │
│                  PID: runs 24/7, ticks every 60s             │
│                                                              │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │
│  │ GH Resp  │  │ GH PR     │  │ Research  │  │ Blog     │  │
│  │ every 1h │  │ every 2.5h│  │ every 4h  │  │ every 12h│  │
│  └────┬─────┘  └────┬──────┘  └────┬──────┘  └────┬─────┘  │
│       │              │              │              │         │
│       ▼              ▼              ▼              ▼         │
│  [wake-gate]    [wake-gate]    [wake-gate]    [wake-gate]    │
│  gh search prs  gh search      glob outputs   check blog/   │
│  + activity     issues         ~/research     exists         │
│  marker         (labels)       + freshness                   │
│       │              │              │              │         │
│  wakeAgent?     wakeAgent?     wakeAgent?     wakeAgent?    │
│       │              │              │              │         │
│     false→skip  false→skip    false→skip        true        │
│     true↓        true↓          true↓             ↓         │
│       ▼              ▼              ▼              ▼         │
│  ┌───────────────────────────────┐ ┌──────────────────────┐ │
│  │  SCRIPT calls codex exec      │ │  KIMI K2.6 (Lacia)   │ │
│  │  gpt-5.5 / xhigh              │ │  Hermes AIAgent      │ │
│  │  workspace-write sandbox      │ │                      │ │
│  │  cwd: ~/workspace             │ │  delegate(Step)→     │ │
│  │  or experiment dir             │ │   web search topics  │ │
│  │                               │ │  delegate(MiniMax)→  │ │
│  │  pr-followup spec             │ │   write blog post    │ │
│  │  github-pr spec               │ │  terminal()→         │ │
│  │  exp-run spec                 │ │   pnpm build         │ │
│  │                               │ │   git commit+push    │ │
│  │  ┌─────────────────────────┐  │ │                      │ │
│  │  │ CODEX CLI              │  │ └──────────────────────┘ │
│  │  │ Primary executor:      │  │        Hermes Native     │
│  │  │ code, review, PRs,    │  │                           │
│  │  │ experiments            │  │                           │
│  │  │ Runs 30min-2h          │  │                           │
│  │  └─────────────────────────┘  │                           │
│  └───────────────────────────────┘                           │
│        Script → Codex direct                                 │
│        (no Hermes agent middleman)                           │
│                                                              │
│  After script completes:                                     │
│  → Output fed to Kimi for summarize + memory save (~3 turns) │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Fixes Applied

1. **KIMI_BASE_URL double /v1**: `https://api.kimi.com/coding/v1` in `.env` caused the Anthropic SDK to build `…/v1/v1/messages` (404). Fixed to `https://api.kimi.com/coding`. The SDK appends `/v1/messages` itself.

2. **Model name format**: `"kimi k2.6"` (with space) → `"kimi-k2.6"` (hyphenated). Hermes expects hyphenated model IDs.

3. **Step provider**: No built-in `step` provider. Added as named custom provider in `providers:` section with `key_env: STEPFUN_API_KEY`.

4. **Delegation provider**: `custom` not supported for delegation. Changed to named provider `"step"` which resolves through the `providers:` dict.

5. **`.env` symlink**: Broke symlink from `~/.hermes/.env → ~/claw/.env` because the shared `.env` has provider settings used by other tools. Hermes needs its own provider-specific base URL handling.

---

## End-to-End Test Results

| Pipeline | Test Date | Result | Notes |
|----------|-----------|--------|-------|
| GitHub Response | 2026-04-22 | **PASS** | Checked 10 PRs, responded to 2 (ramalama#2646, torchtitan#3023), skipped 8 correctly |
| GitHub PR | 2026-04-22 | **PASS** | Selected Linkora-social#3, implemented fix + tests, submitted [PR#12](https://github.com/Epta-Node/Linkora-social/pull/12) — Codex/Gemini/Security all 10/10 |
| Auto Research | 2026-04-22 | **PASS** | Correctly returned `wakeAgent: false` (no outputs in ~/research yet) |
| Blog Maintenance | 2026-04-22 | **PASS** | Wake-gate detects blog dir, returns prompt for Hermes native |

### Improvements Applied During Testing

1. **GitHub PR search quality**: Changed from `--label=good first issue,help wanted,bug` (returns spam repos) to per-language filtered search across Python, Rust, Go, JS, TS with deduplication
2. **Workspace routing**: Added `contrib/` and `pr-stage/` subdirectories with routing anchors in prompt for structured workspace organization
3. **Agent integration**: PR pipeline prompt now references codex:codex-rescue for implementation and gemini:gemini-consult for architecture checks

---

## Remaining Work

### Phase 2: Native Jobs
- [ ] Create Hermes `blog-maintenance` skill (YAML frontmatter + instructions)
- [ ] Test blog job end-to-end with MiniMax writing + image gen
- [ ] Create `stock-review` skill (future)

### Phase 3: Codex Integration
- [x] GitHub Response pipeline — verified end-to-end (2026-04-22)
- [x] Auto Research wake-gate — verified logic correct (2026-04-22)
- [x] GitHub PR pipeline — verified end-to-end, PR#12 submitted (2026-04-22)
- [ ] Tune `max-turns` per job for cost control
- [ ] Add `gh status` mentions monitoring (currently only tracks authored PRs)

### Phase 4: Delivery & Monitoring
- [ ] Set up Telegram bot for notifications
- [ ] Configure `--deliver telegram` on cron jobs
- [ ] Set up log monitoring: `journalctl --user -u hermes-gateway -f`

### Phase 5: Memory & Evolution
- [ ] Seed `~/.hermes/MEMORY.md` with initial context (portfolio, blog topics, research areas)
- [ ] Create `~/.hermes/shared/queue.md` task queue
- [ ] Test cross-session memory recall

---

## Quick Reference

```bash
# Interactive chat
hermes

# Single query (default Kimi K2.6)
hermes chat -q "your question"

# Switch models
hermes chat -q "..." --model step          # Step 3.5 Flash
hermes chat -q "..." --model MiniMax-M2.7 --provider minimax  # MiniMax M2.7

# Cron management
hermes cron list                  # Show all jobs
hermes cron run <job_id>          # Trigger immediately on next tick
hermes cron tick                  # Manual tick (runs due jobs)
hermes cron pause <job_id>        # Pause a job
hermes cron resume <job_id>       # Resume a job

# Gateway
hermes gateway status             # Check if running
hermes gateway start              # Start service
hermes gateway stop               # Stop service
journalctl --user -u hermes-gateway -f  # Live logs

# Sessions
hermes sessions list              # Past conversations
hermes --resume <session_id>      # Resume a session
```
