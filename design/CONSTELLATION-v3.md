# Constellation v3 — Hybrid: Hermes Native + ClaudeCode Routed

> Version 0.3 — Final Design
> Key insight: use each system for what it's actually good at

## The Split

| Domain | Engine | Why |
|--------|--------|-----|
| **Blog** | Hermes native (MiniMax M2.7) | MiniMax writes well + image-01 for illustrations + full modpack |
| **Stock Review** (future) | Hermes native (Step + Kimi) | Step searches fast, Kimi analyzes, Hermes remembers history |
| **PR Pipeline** | ClaudeCode (routed) | Already built as `/github-pr` command. Needs Codex, Gemini, GSD |
| **Research** | ClaudeCode (routed) | Already built as `/research-analyze`. Needs Agent Teams, Zotero MCP |
| **Memory & Evolution** | Hermes native | This is what Hermes does best — persist, learn, improve |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HERMES AGENT                          │
│              (long-lived companion)                      │
│                                                          │
│  Memory: MEMORY.md + state.db (FTS5 session search)     │
│  Skills: self-improving, 100+ built-in                   │
│  Gateway: Telegram / Discord (human interface)           │
│  Cron: heartbeat scheduler                               │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Kimi K2.6│  │Step 3.5  │  │MiniMax   │              │
│  │ (Lacia)  │  │ (Methode)│  │ M2.7     │              │
│  │          │  │          │  │ (Kouka)  │              │
│  │ orchestr.│  │ tools +  │  │ writing +│              │
│  │ planning │  │ search   │  │ images + │              │
│  │ review   │  │ execute  │  │ TTS/video│              │
│  └──────────┘  └──────────┘  └──────────┘              │
│        │              │              │                    │
│        └──────────────┼──────────────┘                   │
│                       │                                  │
│              NATIVE JOBS                                 │
│              ├── Blog Maintenance (Kouka)                │
│              └── Stock Review (future)                   │
│                                                          │
│              ROUTED JOBS (via cron script)               │
│              ├── PR Pipeline → ClaudeCode                │
│              └── Research → ClaudeCode                   │
└─────────────────────────────────────────────────────────┘
                        │
                        │ cron triggers
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    CLAUDE CODE                           │
│              (powerful executor, on-demand)              │
│                                                          │
│  /github-pr          — 12-phase PR pipeline              │
│  /research-analyze   — Agent Teams research              │
│  /research-init      — Zotero literature review          │
│  /code-review        — Security + quality review         │
│  /analyze-results    — Experiment analysis               │
│                                                          │
│  Plugins: Codex 5.3, Gemini 3.1 Pro, GSD, MCP           │
│  Agents: 23 specialized (code-reviewer, data-analyst...) │
└─────────────────────────────────────────────────────────┘
```

---

## Model-to-Name Mapping

The Beatless names map to the 3-model team's strengths:

| Name | Model | Role | Native Jobs |
|------|-------|------|-------------|
| **Lacia** | Kimi K2.6 | Orchestration, planning, code review | Coordinates all jobs, reviews blog quality |
| **Methode** | Step 3.5 Flash | Tool execution, web search, fast tasks | Searches topics, checks links, gathers data |
| **Kouka** | MiniMax M2.7 | Writing, image gen, TTS, video, docs | Blog writing, illustration, presentation |
| **Snowdrop** | ClaudeCode | Deep research, literature, experiments | Routed: `/research-analyze`, `/research-init` |
| **Saturnus** | ClaudeCode | Code review, PR pipeline, quality gates | Routed: `/github-pr`, `/code-review` |

Snowdrop and Saturnus are not Hermes models — they're **identities** for ClaudeCode sessions triggered by Hermes cron. Their personality contexts (SOUL.md) are passed as `--system-prompt` when ClaudeCode is invoked.

---

## Native Job: Blog Maintenance (Kouka)

This runs entirely inside Hermes using the 3-model team.

### Why Hermes is better here

- MiniMax M2.7 writes well and has native image generation (`image-01`)
- Can generate custom blog illustrations (cartoon, infographic, diagrams)
- Can generate TTS audio versions of posts
- Step 3.5 Flash searches for trending topics, checks links
- Kimi K2.6 reviews quality before publishing
- Hermes remembers blog history, past topics, reader feedback in MEMORY.md

### Execution Flow (cron: every 12h)

```
Hermes cron tick
  │
  ├── Kimi (Lacia): Read queue.md, decide what to write
  │   └── delegate_task(
  │         goal="Search trending AI agent topics this week",
  │         toolsets=["web", "terminal"],
  │         context="Step 3.5 Flash for web search"
  │       )
  │       → Methode (Step): web_search + web_extract → topic list
  │
  ├── Kimi (Lacia): Pick best topic, outline the post
  │   └── delegate_task(
  │         goal="Write blog post on: <topic>",
  │         toolsets=["file", "terminal"],
  │         context="MiniMax M2.7 for content creation"
  │       )
  │       → Kouka (MiniMax): write content to ~/claw/blog/src/content/
  │
  ├── Kimi (Lacia): Review quality
  │   └── If quality < threshold → iterate with MiniMax
  │
  ├── Image generation (MiniMax image-01 API):
  │   └── Generate blog header illustration
  │   └── Generate any inline diagrams
  │
  ├── Verify: terminal → cd ~/claw/blog && pnpm build
  │
  └── Publish: terminal → git add, commit, push
```

### Blog Skill (Hermes native)

```yaml
---
name: blog-maintenance
description: Full blog maintenance cycle with MiniMax writing + image generation
tags: [blog, writing, minimax]
model: kimi k2.6
---

## Blog Maintenance Cycle

You are Kouka, the delivery authority. Execute the blog maintenance cycle:

### Phase 1: Topic Discovery (delegate to Step)
Use delegate_task with toolset ["web"] to search for:
- Trending topics in AI agents, BCI research, LLM engineering
- Topics from ~/.hermes/shared/queue.md
- Topics that complement existing blog posts

### Phase 2: Content Writing (delegate to MiniMax)
Use delegate_task to write the post:
- Follow blog format: Astro MDX with frontmatter
- Include code examples where relevant
- Natural tone, not AI-sounding
- Save to ~/claw/blog/src/content/blogs/<slug>/index.mdx

### Phase 3: Illustration
Use MiniMax image-01 to generate:
- Blog header image (16:9, relevant to topic)
- Any inline diagrams or concept illustrations
- Save to ~/claw/blog/src/content/blogs/<slug>/

### Phase 4: Quality Review
Review the post for:
- Technical accuracy
- Natural language (no AI patterns)
- Working code examples
- Proper frontmatter (title, date, tags, description)

### Phase 5: Build & Publish
```bash
cd ~/claw/blog && pnpm build  # must exit 0
git add -A && git commit -m "feat(blog): <title>" && git push
```

### Stop-Loss
- Build fails → revert, report via Telegram
- Quality < 7/10 after 2 iterations → shelve draft, report
```

---

## Native Job: Stock Review (Future)

Runs inside Hermes. Designed for expansion later.

### Why Hermes is better here

- Step 3.5 Flash: fast web search for stock data, news, filings
- Kimi K2.6: analysis, pattern recognition, risk assessment
- Hermes memory: remembers your portfolio, past analyses, preferences
- MiniMax: generate summary reports, charts, audio briefings

### Execution Flow (cron: daily at market close)

```
Hermes cron tick
  │
  ├── Step (Methode): Search stock data, news, filings
  │   └── web_search + web_extract for each tracked ticker
  │
  ├── Kimi (Lacia): Analyze + compare against memory
  │   └── Read MEMORY.md for portfolio history
  │   └── Compute changes, flag anomalies
  │
  ├── MiniMax (Kouka): Generate report
  │   └── Write formatted summary
  │   └── Optional: TTS audio briefing
  │
  └── Deliver via Telegram
```

---

## Routed Job: PR Pipeline → ClaudeCode

Hermes triggers, ClaudeCode executes.

### Cron Script

```python
#!/usr/bin/env python3
"""PR Pipeline — Hermes cron wake-gate + ClaudeCode dispatch."""
import subprocess, json, sys, os

# Wake-gate: check if there are open issues to work on
result = subprocess.run(
    ["gh", "search", "issues",
     "--label=good-first-issue,help-wanted,bug",
     "--state=open", "--sort=updated", "--limit=5",
     "--json=title,url,repository"],
    capture_output=True, text=True, timeout=30
)

issues = json.loads(result.stdout) if result.stdout.strip() else []
if not issues:
    print(json.dumps({"wakeAgent": False}))
    sys.exit(0)

# Context from Hermes memory (passed via env or file)
# Hermes can write recent context to a temp file before script runs

# Execute in ClaudeCode
soul = open(os.path.expanduser("~/claw/Beatless/agents/saturnus/SOUL.md")).read()
result = subprocess.run(
    ["claude", "--print",
     "--model", "claude-sonnet-4-6",
     "--max-turns", "50",
     "--system-prompt", soul,
     "Execute /github-pr pipeline. "
     f"Candidate issues: {json.dumps(issues[:3])}"],
    capture_output=True, text=True,
    timeout=3600,
    cwd=os.path.expanduser("~/workspace")
)

print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
```

---

## Routed Job: Research → ClaudeCode

### Cron Script

```python
#!/usr/bin/env python3
"""Auto-Research — Hermes cron wake-gate + ClaudeCode dispatch."""
import subprocess, json, sys, os

# Wake-gate: check if experiments have new results
exp_dir = os.path.expanduser("~/claw/<experiment-repo>/outputs/")
if not os.path.exists(exp_dir):
    print(json.dumps({"wakeAgent": False}))
    sys.exit(0)

# Check for results newer than last analysis
# (simple: check mtime of latest output vs last-analyzed marker)
marker = os.path.expanduser("~/.hermes/shared/.last-research-analysis")
latest_output = max(
    (os.path.join(exp_dir, f) for f in os.listdir(exp_dir)),
    key=os.path.getmtime, default=None
)
if latest_output and os.path.exists(marker):
    if os.path.getmtime(latest_output) < os.path.getmtime(marker):
        print(json.dumps({"wakeAgent": False}))
        sys.exit(0)

soul = open(os.path.expanduser("~/claw/Beatless/agents/snowdrop/SOUL.md")).read()
result = subprocess.run(
    ["claude", "--print",
     "--model", "claude-sonnet-4-6",
     "--max-turns", "30",
     "--system-prompt", soul,
     "Execute /research-analyze on the latest experiment outputs. "
     "Compare against baselines. Generate analysis report."],
    capture_output=True, text=True,
    timeout=3600,
    cwd=os.path.expanduser("~/claw/<experiment-repo>")
)

# Touch marker
open(marker, "w").close()

print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
```

---

## Hermes as the Memory Layer

This is Hermes's real superpower. Across ALL jobs (native and routed), Hermes:

### Remembers Everything

```
~/.hermes/MEMORY.md (persistent, agent-edited)
├── Portfolio: tracked stocks, thresholds, past analyses
├── Blog: published topics, reader feedback, content calendar
├── GitHub: active PRs, maintainer preferences, repo evaluations
├── Research: experiment status, hypotheses, results history
└── Preferences: writing style, review standards, risk tolerance

~/.hermes/state.db (automatic, FTS5 searchable)
├── Every conversation transcript
├── Every cron job output
├── Searchable with /search across all sessions
└── Cross-session recall for long-term patterns
```

### Learns and Improves Skills

After each job execution, Hermes can:
1. **Evaluate what worked** — Did the blog post get published? Did the PR get merged?
2. **Update skills** — Refine blog writing style, improve research prompts
3. **Remember context** — "Last time we fixed a marvin issue, the maintainer wanted X"

### Provides Context to ClaudeCode

When Hermes triggers a ClaudeCode job, it can inject memory context:

```python
# In the cron script, before calling claude:
memory = subprocess.run(
    ["hermes", "memory", "search", "github marvin maintainer preferences"],
    capture_output=True, text=True
)
# Pass as context to ClaudeCode
claude_prompt = f"""
Context from past sessions:
{memory.stdout}

Execute /github-pr pipeline...
"""
```

### User Preference Learning

Hermes builds a model of you over time:
- "User prefers concise blog posts under 1500 words"
- "User wants stock analysis focused on AI/semiconductor sectors"
- "User reviews PR feedback within 2 hours of notification"
- "User's research focuses on BCI + neural decoding"

This shapes all future interactions — both native jobs and routed ClaudeCode prompts.

---

## Cron Configuration

### 4 Jobs

```bash
# Blog (Hermes native — uses MiniMax + Step + Kimi internally)
hermes cron add "Blog Maintenance" \
  --schedule "every 12h" \
  --deliver telegram \
  --skill blog-maintenance \
  --prompt "Run the blog maintenance cycle. Check queue, write if needed, publish."

# Stock Review (Hermes native — future)
hermes cron add "Stock Review" \
  --schedule "0 21 * * 1-5" \
  --deliver telegram \
  --skill stock-review \
  --prompt "Daily market close review for tracked portfolio."

# PR Pipeline (routed to ClaudeCode)
hermes cron add "GitHub PR Pipeline" \
  --schedule "every 150m" \
  --deliver telegram \
  --script ~/.hermes/scripts/github-pr.py

# Research (routed to ClaudeCode)
hermes cron add "Auto Research" \
  --schedule "every 4h" \
  --deliver telegram \
  --script ~/.hermes/scripts/auto-research.py
```

### Key difference: `--skill` vs `--script`

- `--skill` → Hermes runs the job as a native AI conversation with the skill loaded. Uses Kimi/Step/MiniMax. Best for blog, stock, anything Hermes can do well.
- `--script` → Hermes runs a Python script that calls ClaudeCode externally. Zero Hermes model tokens. Best for PR, research.

---

## Model Routing in Hermes

Hermes needs to route different tasks to different models within a single session.
This is done via `delegate_task` with model-specific toolsets:

### In `config.yaml`:

```yaml
# Default orchestrator
model: kimi k2.6
provider: custom
base_url: https://api.kimi.com/coding/v1
api_key: ${KIMI_API_KEY}

# Delegation routes tasks to Step for execution
delegation:
  provider: custom
  base_url: https://api.stepfun.com/step_plan/v1
  api_key: ${STEPFUN_API_KEY}
  model: step-3.5-flash
  max_concurrent_children: 5
  max_spawn_depth: 2
  orchestrator_enabled: true
```

### MiniMax routing

MiniMax isn't natively supported as a delegation target in the current Hermes config.
Two options:

**Option A**: Use MiniMax as the primary model for blog jobs:
```bash
hermes cron add "Blog Maintenance" \
  --model "MiniMax-M2.7" \
  --provider custom \
  --base-url "https://api.minimaxi.com/anthropic" \
  ...
```

**Option B**: Call MiniMax API via `terminal` tool during blog skill:
```bash
# In blog-maintenance skill, for image generation:
curl -X POST https://api.minimaxi.com/v1/images/generations \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -d '{"model":"image-01","prompt":"..."}'
```

---

## Summary: What Each System Does

### Hermes Agent
- **Schedules** all jobs (cron)
- **Delivers** results (Telegram/Discord)
- **Remembers** everything (memory + session search)
- **Learns** user preferences over time
- **Improves** its own skills after each run
- **Executes natively**: Blog (MiniMax writing + images), Stock (Step search + Kimi analysis)
- **Routes to ClaudeCode**: PR pipeline, Research

### ClaudeCode
- **Executes** complex multi-step pipelines (PR, research)
- **Uses** its full ecosystem (Codex, Gemini, GSD, MCP, Agent Teams)
- **Already has** all commands built (`/github-pr`, `/research-analyze`, etc.)
- **Triggered by** Hermes cron scripts
- **Returns** results to Hermes for delivery + memory storage

### The 3-Model Team (inside Hermes)
- **Kimi K2.6 (Lacia)**: Orchestrates, plans, reviews — the brain
- **Step 3.5 Flash (Methode)**: Searches, executes tools, gathers data — the hands
- **MiniMax M2.7 (Kouka)**: Writes, generates images/audio/video — the voice

---

## Migration from Beatless v2.1

| Component | v2.1 (Current) | v3 (Target) | Action |
|-----------|----------------|-------------|--------|
| Scheduler | bash cron-driver.sh | Hermes cron | Replace |
| PR pipeline spec | pipelines/github-pr.md | ClaudeCode `/github-pr` | Already exists |
| Blog skill | pipelines/blog-maintenance.md | Hermes skill (blog-maintenance) | Rewrite as Hermes skill |
| SOUL.md files | agents/*/SOUL.md | Hermes personality + ClaudeCode --system-prompt | Keep, adapt |
| Mailbox | JSONL files | queue.md (simple) | Simplify |
| Harness scripts | checkpoint, verify, safety | Keep for ClaudeCode routes | Keep |
| Agent identities | 6 separate processes | 3 Hermes models + 2 ClaudeCode roles | Consolidate |
