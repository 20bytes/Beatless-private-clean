# Constellation — Native Hermes Multi-Agent Orchestration

> Version 0.1 — Design Document
> Supersedes: Beatless v2.1 (external bash/SOUL.md orchestration)

## Vision

Five autonomous Hermes agents — **Lacia, Kouka, Methode, Snowdrop, Saturnus** — each running as a full Hermes profile with its own identity, memory, skills, and evolution loop. They communicate through a shared mailbox, coordinate through pipeline state machines, and continuously improve through Hermes's native skill system.

No external bash harness. No `claude --print` routing. Each agent IS a Hermes instance.

---

## Architecture: Two Patterns, One System

### Pattern A: Constellation (5 Peer Agents)

```
                    ┌─────────────┐
                    │   Mailbox   │
                    │  (shared)   │
                    └──────┬──────┘
           ┌───────┬───────┼───────┬───────┐
           ▼       ▼       ▼       ▼       ▼
      ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
      │ Lacia  ││ Kouka  ││Methode ││Snowdrop││Saturnus│
      │Strategy││Delivery││Execute ││Research││ Review │
      │        ││        ││        ││        ││        │
      │ cron   ││ cron   ││ cron   ││ cron   ││ cron   │
      │ memory ││ memory ││ memory ││ memory ││ memory │
      │ skills ││ skills ││ skills ││ skills ││ skills │
      └────────┘└────────┘└────────┘└────────┘└────────┘
        Profile    Profile   Profile   Profile   Profile
```

Each agent is a `hermes -p <name>` process with:
- Its own `~/.hermes/profiles/<name>/` (config, memory, skills, sessions)
- Its own personality (SOUL.md loaded as context file)
- Its own cron schedule (heartbeat + domain-specific jobs)
- Its own skill library (self-created, self-improved)
- Shared mailbox at `~/.hermes/shared/mailbox/`
- Shared pipeline state at `~/.hermes/shared/pipelines/`

### Pattern B: Delegation Swarm (Orchestrator + Workers)

Any Constellation agent can spawn short-lived subagents via `delegate_task`:

```
Methode (Profile, long-lived)
  │
  ├── delegate_task(goal="Fix the bug in auth.py", toolset=["terminal","file"])
  │     └── Subagent 0 (ephemeral, isolated, leaf)
  │
  ├── delegate_task(tasks=[
  │     {goal: "Run test suite", toolset: ["terminal"]},
  │     {goal: "Lint check",     toolset: ["terminal"]},
  │     {goal: "Type check",     toolset: ["terminal"]}
  │   ])
  │     ├── Subagent 1 (parallel)
  │     ├── Subagent 2 (parallel)
  │     └── Subagent 3 (parallel)
  │
  └── (reports result to mailbox)
```

**Pattern A** = social layer (long-lived identity, memory, evolution)
**Pattern B** = execution layer (short-lived workers, no memory, disposable)

---

## The Five Agents

### 1. Lacia — Convergence Authority

| Field | Value |
|-------|-------|
| Profile | `hermes -p lacia` |
| Model | Kimi K2.6 (planning/reasoning) |
| Toolsets | `terminal, file, web, delegation` |
| Heartbeat | Every 30 min |
| Domain | Strategy, planning, requirement decomposition |

**Constitutional Power**: Narrative rewrite right. Can reframe the task definition when the framing itself is the problem.

**Cron Jobs**:
- `heartbeat` (30min): Read mailbox, process task_requests, update pipeline state
- `convergence-check` (2h): Review active pipelines for stalls, propose unblocking strategies
- `skill-audit` (daily): Review own skill library, propose improvements

**Delegation Pattern**: Spawns subagents for plan decomposition, requirement clarification, milestone creation. Orchestrator role — can spawn sub-planners for parallel requirement analysis.

**Self-Evolution Focus**: Planning templates, decomposition heuristics, estimation accuracy.

---

### 2. Kouka — Delivery Authority

| Field | Value |
|-------|-------|
| Profile | `hermes -p kouka` |
| Model | Step 3.5 Flash (fast execution) |
| Toolsets | `terminal, file, web, delegation` |
| Heartbeat | Every 30 min |
| Domain | Blog, PR submission, artifact packaging, stop-loss |

**Constitutional Power**: Fast-track right and tie-break right. Cuts the knot when the system deadlocks.

**Cron Jobs**:
- `heartbeat` (30min): Read mailbox, process delivery requests
- `blog-maintenance` (12h): Audit blog, write/edit posts, verify build
- `delivery-sweep` (4h): Check for stalled deliverables, apply stop-loss rules

**Delegation Pattern**: Spawns subagents for blog writing, PR formatting, build verification. Leaf workers only — Kouka makes all delivery decisions directly.

**Self-Evolution Focus**: Blog writing quality, PR template patterns, delivery checklist refinement.

**Stop-Loss Rules**:
- Task stalled >24h with no progress → mark `wontfix`, notify Lacia
- 2 consecutive no-progress heartbeats → trigger stop-loss
- Stop-loss is a delivery outcome, not a refusal

---

### 3. Methode — Execution Specialist

| Field | Value |
|-------|-------|
| Profile | `hermes -p methode` |
| Model | Step 3.5 Flash (fast, zero hallucination) |
| Toolsets | `terminal, file, web, browser, delegation, code` |
| Heartbeat | Every 30 min |
| Domain | Implementation, debugging, artifact generation |

**Constitutional Power**: Execution takeover right. When a task is blocked, Methode owns the unblocking attempt.

**Cron Jobs**:
- `heartbeat` (30min): Read mailbox, execute implementation tasks
- `unblock-sweep` (1h): Check for HOLD verdicts, attempt automatic fixes

**Delegation Pattern**: Heavy user of parallel delegation. Spawns multiple subagents for:
- Parallel test suites across modules
- Multi-file refactoring (one subagent per file)
- Bug reproduction + fix verification simultaneously

**Self-Evolution Focus**: Debugging strategies, implementation patterns, test generation templates.

---

### 4. Snowdrop — Research & Discovery

| Field | Value |
|-------|-------|
| Profile | `hermes -p snowdrop` |
| Model | Kimi K2.6 (deep reasoning, 128K context) |
| Toolsets | `terminal, file, web, browser, delegation` |
| Heartbeat | Every 30 min |
| Domain | GitHub discovery, literature research, ecosystem scanning |

**Constitutional Power**: Forced alternative injection. Must always surface at least one path the group isn't considering.

**Cron Jobs**:
- `heartbeat` (30min): Read mailbox, process research requests
- `github-hunt` (8h): Discover fixable issues in target repos
- `trend-scan` (daily): Scan AI/agent ecosystem for relevant developments

**Delegation Pattern**: Spawns parallel scanners — one per repository or research question. Orchestrator role — scanner subagents can delegate to focused analyzers.

**Self-Evolution Focus**: Search strategies, repository evaluation heuristics, research synthesis templates.

---

### 5. Saturnus — Review Gate

| Field | Value |
|-------|-------|
| Profile | `hermes -p saturnus` |
| Model | Kimi K2.6 (careful reasoning) |
| Toolsets | `terminal, file, web, delegation` |
| Heartbeat | Every 30 min |
| Domain | Code review, quality gates, evidence auditing |

**Constitutional Power**: Strong veto and compliance gate. A REJECT stops the pipeline until resolved.

**Cron Jobs**:
- `heartbeat` (30min): Read mailbox, process review requests
- `evidence-audit` (2h): Cross-reference claimed changes against actual git diffs

**Delegation Pattern**: Spawns parallel reviewers for multi-perspective analysis:
- Correctness reviewer (does the code work?)
- Architecture reviewer (is the design sound?)
- Security reviewer (any vulnerabilities?)
- All three run concurrently; Saturnus merges verdicts

**Verdict Policy**:
- **PASS** → artifact continues to delivery (Kouka)
- **HOLD** → need more evidence; explicit override required
- **REJECT** → Methode must fix P0/P1 issues before resubmission

**Self-Evolution Focus**: Review rubrics, severity classification accuracy, false-positive reduction.

---

## Shared Infrastructure

### Mailbox System

Location: `~/.hermes/shared/mailbox/`

Each agent has a `.jsonl` file (append-only log):
```
~/.hermes/shared/mailbox/
├── lacia.jsonl
├── kouka.jsonl
├── methode.jsonl
├── snowdrop.jsonl
├── saturnus.jsonl
└── broadcast.jsonl    # messages to all agents
```

**Message Envelope**:
```json
{
  "id": "msg_20260422_001",
  "type": "task_request | task_result | review_verdict | message | alert | evolution_report",
  "from": "snowdrop",
  "to": "methode",
  "subject": "Fix auth token refresh in marvin#950",
  "body": {
    "pipeline": "github-pr",
    "phase": "IMPLEMENT",
    "context": { ... },
    "deadline_at": "2026-04-22T18:00:00Z"
  },
  "correlation_id": "corr_20260422_001",
  "created_at": "2026-04-22T14:30:00Z",
  "read": false
}
```

**New Message Types** (vs Beatless v2.1):
- `evolution_report` — agent reports a skill it created/improved, others can adopt
- `capability_query` — agent asks "who can handle X?" before routing
- `state_sync` — pipeline state checkpoint broadcast

**Implementation**: The existing `mail.mjs` script continues to work. Agents call it via `terminal` tool during their heartbeat. No new infrastructure needed.

### Pipeline State Machines

Location: `~/.hermes/shared/pipelines/`

```
~/.hermes/shared/pipelines/
├── github-pr/
│   ├── state.json         # Current pipeline state
│   └── history.jsonl      # Completed run log
├── blog-maintenance/
│   ├── state.json
│   └── history.jsonl
├── github-hunt/
│   ├── state.json
│   └── history.jsonl
└── registry.json          # Pipeline definitions + ownership
```

**`registry.json`** — defines which agent owns each pipeline phase:
```json
{
  "github-pr": {
    "phases": {
      "DISCOVER":  { "owner": "snowdrop", "timeout_min": 60 },
      "EVALUATE":  { "owner": "snowdrop", "timeout_min": 30 },
      "PLAN":      { "owner": "lacia",    "timeout_min": 30 },
      "IMPLEMENT": { "owner": "methode",  "timeout_min": 180 },
      "VERIFY":    { "owner": "methode",  "timeout_min": 60 },
      "REVIEW":    { "owner": "saturnus", "timeout_min": 60 },
      "DELIVER":   { "owner": "kouka",    "timeout_min": 60 }
    },
    "interval_hours": 2.5,
    "initiator": "snowdrop"
  }
}
```

### Shared Scripts

Location: `~/.hermes/shared/scripts/`

Existing scripts from Beatless v2.1 are reused unchanged:

| Script | Purpose |
|--------|---------|
| `mail.mjs` | Mailbox CRUD (read/send/mark/count) |
| `checkpoint.mjs` | Git checkpoint refs |
| `session-lock.mjs` | O_EXCL agent locking (prevents 2 agents on same task) |
| `metrics.mjs` | Token/cost ledger |
| `verify.mjs` | Post-execution test runner |
| `safety.mjs` | Evidence audit (git diff vs claims) |

---

## Self-Evolution System

Each agent has an evolution loop built on Hermes's native skill system:

### Evolution Cycle

```
                ┌──────────────────┐
                │   Task Execution │
                └────────┬─────────┘
                         │
                    Did I learn
                   something new?
                    ┌────┴────┐
                    │ YES     │ NO
                    ▼         ▼
            ┌──────────┐   (continue)
            │ Skill    │
            │ Creation │
            │ or       │
            │ Update   │
            └────┬─────┘
                 │
                 ▼
          ┌──────────────┐
          │ evolution    │
          │ _report to   │
          │ broadcast    │
          │ mailbox      │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │ Other agents │
          │ can adopt    │
          │ the skill    │
          └──────────────┘
```

### Skill Locations

Each profile has its own skill directory:
```
~/.hermes/profiles/lacia/skills/
├── plan-decomposition.md        # Self-created
├── requirement-clarification.md # Self-created
├── milestone-estimation.md      # Self-created
└── adopted/
    └── security-review-rubric.md  # Adopted from Saturnus
```

### Evolution Report Message

When an agent creates or improves a skill:
```json
{
  "type": "evolution_report",
  "from": "saturnus",
  "to": "broadcast",
  "subject": "Improved: security-review-rubric v3",
  "body": {
    "skill_name": "security-review-rubric",
    "action": "improved",
    "version": 3,
    "summary": "Added OWASP Top 10 2025 checks, reduced false positives by 40%",
    "path": "~/.hermes/profiles/saturnus/skills/security-review-rubric.md"
  }
}
```

Other agents can adopt skills during their heartbeat:
```bash
# In heartbeat cron, after reading broadcast mailbox:
cp ~/.hermes/profiles/saturnus/skills/security-review-rubric.md \
   ~/.hermes/profiles/methode/skills/adopted/
```

---

## Profile Setup

### Directory Structure (per agent)

```
~/.hermes/profiles/<name>/
├── config.yaml          # Model, provider, toolsets, personality
├── .env                 # API keys (shared via symlink)
├── MEMORY.md            # Agent-specific persistent memory
├── SOUL.md              # Personality + constitutional powers (context file)
├── context/
│   └── HERMES.md        # Shared protocol (symlinked)
├── skills/              # Agent-specific skills
│   ├── <domain-skills>  # Self-created
│   └── adopted/         # Adopted from other agents
├── state.db             # Session history (FTS5)
└── cron/
    └── jobs.json        # Cron schedule
```

### Bootstrap: `config.yaml` per Agent

**Lacia** (Strategy):
```yaml
model: kimi k2.6
provider: custom
base_url: https://api.kimi.com/coding/v1
api_key: ${KIMI_API_KEY}

personality: lacia
context_files:
  - SOUL.md
  - context/HERMES.md

delegation:
  provider: custom
  base_url: https://api.stepfun.com/step_plan/v1
  api_key: ${STEPFUN_API_KEY}
  model: step-3.5-flash
  max_concurrent_children: 3
  max_spawn_depth: 2
  orchestrator_enabled: true

tools:
  enabled: [terminal, file, web, delegation]
```

**Methode** (Execution):
```yaml
model: step-3.5-flash
provider: custom
base_url: https://api.stepfun.com/step_plan/v1
api_key: ${STEPFUN_API_KEY}

personality: methode
context_files:
  - SOUL.md
  - context/HERMES.md

delegation:
  max_concurrent_children: 5
  max_spawn_depth: 2
  child_timeout_seconds: 600

tools:
  enabled: [terminal, file, web, browser, delegation, code]
```

**Kouka** (Delivery):
```yaml
model: step-3.5-flash
provider: custom
base_url: https://api.stepfun.com/step_plan/v1
api_key: ${STEPFUN_API_KEY}

personality: kouka
context_files:
  - SOUL.md
  - context/HERMES.md

delegation:
  max_concurrent_children: 3
  max_spawn_depth: 1

tools:
  enabled: [terminal, file, web, delegation]
```

**Snowdrop** (Research):
```yaml
model: kimi k2.6
provider: custom
base_url: https://api.kimi.com/coding/v1
api_key: ${KIMI_API_KEY}

personality: snowdrop
context_files:
  - SOUL.md
  - context/HERMES.md

delegation:
  provider: custom
  base_url: https://api.stepfun.com/step_plan/v1
  api_key: ${STEPFUN_API_KEY}
  model: step-3.5-flash
  max_concurrent_children: 5
  max_spawn_depth: 2
  orchestrator_enabled: true

tools:
  enabled: [terminal, file, web, browser, delegation]
```

**Saturnus** (Review):
```yaml
model: kimi k2.6
provider: custom
base_url: https://api.kimi.com/coding/v1
api_key: ${KIMI_API_KEY}

personality: saturnus
context_files:
  - SOUL.md
  - context/HERMES.md

delegation:
  max_concurrent_children: 3
  max_spawn_depth: 1

tools:
  enabled: [terminal, file, web, delegation]
```

---

## Heartbeat Protocol (Native Hermes Cron)

Each agent runs via `hermes -p <name> cron`:

### Heartbeat Skill (loaded by all agents)

```yaml
---
name: heartbeat
description: Core heartbeat loop — read mailbox, process tasks, update state
tags: [system, heartbeat]
---

## Heartbeat Protocol

Every heartbeat tick, execute this sequence:

1. **Read mailbox**
   ```bash
   node ~/.hermes/shared/scripts/mail.mjs read --agent <my-name> --unread
   ```

2. **Read broadcast**
   ```bash
   node ~/.hermes/shared/scripts/mail.mjs read --agent broadcast --unread
   ```

3. **Process messages** (in priority order):
   - `alert` → handle immediately
   - `task_request` → execute (acquire lock, run, report result)
   - `review_verdict` → update pipeline state, route to next phase
   - `evolution_report` → evaluate skill adoption
   - `message` → respond if needed

4. **Check pipeline schedules**
   - Read `~/.hermes/shared/pipelines/registry.json`
   - For pipelines where I am `initiator` and `next_run < now`:
     - Create task_request for first phase
     - Send to phase owner's mailbox
     - Update pipeline state

5. **Self-evolution check**
   - Did this heartbeat's work teach me something reusable?
   - If yes → create/update skill, send evolution_report to broadcast

6. **Report** (only if there were results or alerts — no idle spam)
```

### Cron Schedule (per agent)

```bash
# Lacia: heartbeat every 30 min + daily convergence audit
hermes -p lacia cron add "heartbeat check" --every 30m
hermes -p lacia cron add "convergence audit" --every 2h
hermes -p lacia cron add "skill self-review" --every 24h

# Kouka: heartbeat + blog cycle
hermes -p kouka cron add "heartbeat check" --every 30m
hermes -p kouka cron add "blog maintenance" --every 12h

# Methode: heartbeat + unblock sweep
hermes -p methode cron add "heartbeat check" --every 30m
hermes -p methode cron add "unblock sweep" --every 1h

# Snowdrop: heartbeat + github discovery + trend scan
hermes -p snowdrop cron add "heartbeat check" --every 30m
hermes -p snowdrop cron add "github issue hunt" --every 8h
hermes -p snowdrop cron add "ecosystem trend scan" --every 24h

# Saturnus: heartbeat + evidence audit
hermes -p saturnus cron add "heartbeat check" --every 30m
hermes -p saturnus cron add "evidence cross-audit" --every 2h
```

---

## Pipeline Flow: GitHub PR (Example)

```
Snowdrop (8h cron)
  │ github-hunt: find 5 candidate repos + issues
  │ delegate_task(tasks=[
  │   {goal: "Evaluate repo A", toolset: ["terminal","file","web"]},
  │   {goal: "Evaluate repo B", toolset: ["terminal","file","web"]},
  │   {goal: "Evaluate repo C", toolset: ["terminal","file","web"]},
  │ ])
  │ → picks best candidate
  │ → mail.mjs send --to lacia --type task_request
  │
  ▼
Lacia (next heartbeat)
  │ reads task_request from mailbox
  │ plans fix strategy, decomposes into steps
  │ → mail.mjs send --to methode --type task_request
  │
  ▼
Methode (next heartbeat)
  │ reads task_request from mailbox
  │ session-lock.mjs acquire
  │ checkpoint.mjs create
  │ delegate_task(tasks=[
  │   {goal: "Reproduce the bug", toolset: ["terminal","file"]},
  │   {goal: "Implement the fix", toolset: ["terminal","file"]},
  │ ])  // sequential — reproduce first, then fix
  │ verify.mjs run
  │ safety.mjs audit
  │ session-lock.mjs release
  │ → mail.mjs send --to saturnus --type task_request (review)
  │
  ▼
Saturnus (next heartbeat)
  │ reads task_request from mailbox
  │ delegate_task(tasks=[
  │   {goal: "Correctness review", toolset: ["terminal","file"]},
  │   {goal: "Architecture review", toolset: ["terminal","file"]},
  │   {goal: "Security review",    toolset: ["terminal","file"]},
  │ ])  // parallel — three perspectives at once
  │ merges verdicts → PASS / HOLD / REJECT
  │ if REJECT → mail.mjs send --to methode (fix P0/P1)
  │ if PASS   → mail.mjs send --to kouka (deliver)
  │
  ▼
Kouka (next heartbeat)
  │ reads task_request from mailbox
  │ verifies review gate artifact exists
  │ formats PR (title, body, labels)
  │ gh pr create (via terminal tool)
  │ → mail.mjs send --to broadcast --type task_result
```

---

## Inter-Agent Conversations

Beyond task routing, agents can hold conversations through the mailbox:

### Direct Message
```bash
# Saturnus asks Methode about a suspicious code pattern
node ~/.hermes/shared/scripts/mail.mjs send \
  --from saturnus --to methode \
  --type message \
  --subject "Question about auth.py:142" \
  --body "The token refresh logic looks like it could race under concurrent requests. Was this intentional, or should I flag it?"
```

### Broadcast Discussion
```bash
# Snowdrop surfaces a finding for everyone
node ~/.hermes/shared/scripts/mail.mjs send \
  --from snowdrop --to broadcast \
  --type message \
  --subject "New framework alert: LangGraph v0.4 dropped" \
  --body "Major API changes affect our evaluation pipeline. Lacia: should we re-plan? Methode: compatibility check needed."
```

### Capability Negotiation
```bash
# Lacia isn't sure who should handle a mixed research+implementation task
node ~/.hermes/shared/scripts/mail.mjs send \
  --from lacia --to broadcast \
  --type capability_query \
  --subject "Who handles: benchmark suite creation?" \
  --body "Need someone who can both research benchmark methodologies AND implement the test harness. Snowdrop? Methode? Joint?"
```

---

## Startup & Operations

### First-Time Bootstrap

```bash
#!/bin/bash
# bootstrap-constellation.sh

AGENTS=("lacia" "kouka" "methode" "snowdrop" "saturnus")
SHARED="$HOME/.hermes/shared"

# 1. Create shared infrastructure
mkdir -p "$SHARED"/{mailbox,pipelines/{github-pr,blog-maintenance,github-hunt},scripts,logs}

# 2. Copy shared scripts (from Beatless repo)
cp Beatless/scripts/harness/*.mjs "$SHARED/scripts/"

# 3. Create profiles
for agent in "${AGENTS[@]}"; do
  hermes -p "$agent" setup --non-interactive
  # Copy SOUL.md as context file
  cp "Beatless/agents/${agent}/SOUL.md" "$HOME/.hermes/profiles/$agent/SOUL.md"
  # Symlink shared protocol
  mkdir -p "$HOME/.hermes/profiles/$agent/context"
  ln -sf "$SHARED/../shared-context/HERMES.md" "$HOME/.hermes/profiles/$agent/context/HERMES.md"
  # Symlink .env
  ln -sf "$HOME/claw/.env" "$HOME/.hermes/profiles/$agent/.env"
  # Initialize mailbox
  touch "$SHARED/mailbox/${agent}.jsonl"
done

# 4. Initialize broadcast mailbox
touch "$SHARED/mailbox/broadcast.jsonl"

# 5. Initialize pipeline registry
cat > "$SHARED/pipelines/registry.json" << 'EOF'
{
  "github-pr": {
    "phases": {
      "DISCOVER":  {"owner":"snowdrop","timeout_min":60},
      "PLAN":      {"owner":"lacia","timeout_min":30},
      "IMPLEMENT": {"owner":"methode","timeout_min":180},
      "VERIFY":    {"owner":"methode","timeout_min":60},
      "REVIEW":    {"owner":"saturnus","timeout_min":60},
      "DELIVER":   {"owner":"kouka","timeout_min":60}
    },
    "interval_hours": 2.5,
    "initiator": "snowdrop"
  },
  "blog-maintenance": {
    "phases": {
      "AUDIT":   {"owner":"kouka","timeout_min":30},
      "WRITE":   {"owner":"kouka","timeout_min":120},
      "REVIEW":  {"owner":"saturnus","timeout_min":60},
      "PUBLISH": {"owner":"kouka","timeout_min":30}
    },
    "interval_hours": 12,
    "initiator": "kouka"
  },
  "github-hunt": {
    "phases": {
      "DISCOVER": {"owner":"snowdrop","timeout_min":60},
      "SCAN":     {"owner":"snowdrop","timeout_min":60},
      "EVALUATE": {"owner":"lacia","timeout_min":30}
    },
    "interval_hours": 8,
    "initiator": "snowdrop"
  }
}
EOF

echo "Constellation bootstrapped. Start agents with:"
for agent in "${AGENTS[@]}"; do
  echo "  hermes -p $agent cron start"
done
```

### Running the Constellation

```bash
# Start all agents (each as a background cron process)
for agent in lacia kouka methode snowdrop saturnus; do
  hermes -p $agent cron start &
done

# Interactive session with a specific agent
hermes -p lacia              # talk to Lacia directly
hermes -p methode            # talk to Methode directly

# Monitor all agents
hermes -p lacia cron status
tail -f ~/.hermes/shared/logs/*.log

# Send a task to any agent via Telegram/Discord gateway
hermes -p snowdrop gateway start  # Snowdrop on Telegram
```

### Stopping the Constellation

```bash
for agent in lacia kouka methode snowdrop saturnus; do
  hermes -p $agent cron stop
done
```

---

## vs Beatless v2.1: What Changed

| Aspect | Beatless v2.1 | Constellation |
|--------|--------------|---------------|
| Agent runtime | Step 3.5 Flash routing → `claude --print` | Native Hermes process per agent |
| Orchestrator | Aoi (central dispatcher) | Peer-to-peer (no single dispatcher) |
| Scheduling | External bash `cron-driver.sh` | Native `hermes cron` |
| Skills | SOUL.md + HERMES.md (static) | Hermes skills (self-improving) |
| Memory | None per agent | Hermes MEMORY.md + state.db per agent |
| Delegation | External CLI subprocesses | Native `delegate_task` with toolset isolation |
| Evolution | None | Skill creation + broadcast adoption |
| Communication | Mailbox (kept) | Mailbox (kept + new message types) |
| Pipeline state | JSON state files (kept) | JSON state files (kept + registry) |
| Harness scripts | Checkpoint, verify, safety (kept) | Checkpoint, verify, safety (kept) |
| Entry point | `bash scripts/cron-driver.sh` | `hermes -p <name> cron start` |
| Interactive access | None | `hermes -p <name>` (full TUI) |
| Gateway access | None | `hermes -p <name> gateway` (Telegram/Discord) |

**What's removed**: Aoi as a separate entity. The dispatcher role is distributed — each agent reads its own mailbox and the pipeline registry to know when it's their turn. No single point of failure.

**What's kept**: Mailbox system, pipeline state machines, harness scripts (checkpoint, verify, safety), constitutional powers, Beatless personality traits.

**What's new**: Self-evolution via skills, per-agent persistent memory, native delegation for parallel work, Hermes TUI/Gateway access to each agent, capability negotiation between peers.

---

## Cost Model

| Agent | Model | Heartbeat Cost (est.) | Heavy Task Cost |
|-------|-------|-----------------------|-----------------|
| Lacia | Kimi K2.6 | ~$0.002/tick | ~$0.05/plan |
| Kouka | Step 3.5 Flash | ~$0.001/tick | ~$0.03/blog post |
| Methode | Step 3.5 Flash | ~$0.001/tick | ~$0.10/implementation |
| Snowdrop | Kimi K2.6 | ~$0.002/tick | ~$0.08/github hunt |
| Saturnus | Kimi K2.6 | ~$0.002/tick | ~$0.04/review |

Idle constellation (no tasks): ~48 heartbeats/day * 5 agents * $0.002 = **~$0.48/day**
Active day (2 PRs + 1 blog): ~**$1.50/day**

---

## Open Questions

1. **Aoi's role**: Should Aoi become a 6th agent (dashboard/notification relay to human), or is the peer model sufficient?

2. **Conflict resolution**: When two agents disagree (e.g., Lacia's plan vs Saturnus's review), who breaks the tie? Current design gives Kouka tie-break right, but a voting mechanism could work too.

3. **Skill adoption policy**: Should agents auto-adopt broadcast skills, or should there be an approval step? Auto-adopt is simpler; approval prevents one agent's bad skill from contaminating others.

4. **Gateway per agent**: Should each agent have its own Telegram bot, or should one gateway route to all 5? One gateway is simpler operationally.

5. **MiniMax integration**: Where does the multimedia capability (TTS, image, video) live? Could be a 6th profile or a shared skill that any agent can invoke.
