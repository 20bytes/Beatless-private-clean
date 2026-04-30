---
description: Initialize experiment workspace. Auto-detects mode from Task.md (full — dual-GPU, long budget) or program.md (quick — single-GPU, short budget). Creates branch, planning files, baseline run, results tracking.
argument-hint: "[Task.md path or run-tag] [--skip-baseline]"
allowed-tools: Bash, Read, Write, Glob, Grep, Agent, Skill, mcp__plugin_gsd_gsd__*
---

# Experiment Init

Initialize a clean, reproducible experiment workspace.

## Step 1: Mode Detection

- If argument is a file path ending in `.md` → read it as Task spec → **Full Mode**
- If argument is a short tag string (e.g. `apr22`) → **Quick Mode**, branch = `autoresearch/<tag>`
- If no argument → scan project root:
  - Task.md present → Full Mode
  - program.md + train.py present → Quick Mode
  - Neither → ask user

## Step 2: Read Context

Read all available context files:
- `README.md`, `program.md` (project description)
- `Task.md` (full mode: objective, baseline, SOTA target, constraints, budget)
- `CLAUDE.md` (project-specific Claude instructions)
- Previous round artifacts if resuming: `progress.md`, `findings.md`, `results.tsv`

**Resume detection**: If `progress.md` exists with completed rounds, this is a resume. Summarize prior state in ≤10 bullets. Do NOT re-run baseline. Proceed to output with resume instructions.

## Step 3: Create Branch

- **Quick mode**: `git checkout -b autoresearch/<tag>` from current HEAD
  - If branch exists → stop, ask for new tag
- **Full mode**: `git checkout -b experiment/<tag>` or use branch specified in Task.md
  - Tag default: `$(date +%b%d | tr '[:upper:]' '[:lower:]')`

## Step 4: Verify Prerequisites

```bash
# Runtime
command -v uv || echo "MISSING: uv"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader

# Data (project-specific paths from Task.md or program.md)
ls -la <data_paths>
```

If anything missing → stop with exact fix commands.

## Step 5: Initialize Planning Files

First try the planning-with-files plugin:
- Skill tool → `planning-with-files:plan`

If unavailable, create manually:
- `task_plan.md`: mode, spec summary, experiment queue
- `findings.md`: header, will accumulate per-round analysis
- `progress.md`: header, GPU state, round counter

## Step 6: Initialize Results Ledger

Quick mode columns:
```
commit	val_bpb	memory_gb	status	description
```

Full mode columns:
```
commit	exp_id	gpu	metric	hard_metric	peak_vram_gb	status	description
```

Do NOT git-add results.tsv (intentionally untracked).

## Step 7: Baseline Run (default on, skip with --skip-baseline)

**Quick mode**:
```bash
timeout 700 uv run train.py > run.log 2>&1
grep "^val_bpb:\|^peak_vram_mb:" run.log
```

**Full mode**:
- Run baseline config from Task.md on GPU0
- Record 3-checkpoint metrics (50%, 80%, final) if budget allows
- Record per-class breakdown if available

Parse metrics, compute memory GB, append baseline row to results.tsv.

## Step 8: Update Planning Files

- `task_plan.md`: setup completed, mode recorded, next experiment queue
- `findings.md`: baseline metrics, hardware notes, data characteristics
- `progress.md`: timestamped setup summary

Use GSD to record baseline metric:
- MCP tool: `mcp__plugin_gsd_gsd__gsd_record_metric` with baseline values
- Fallback: write directly to findings.md

## Step 9: Output

```
Experiment initialized:
  Mode:     [Quick / Full]
  Branch:   [branch name]
  Baseline: [metric] ([memory] GB VRAM)
  GPU:      [device info]
  Budget:   [time per run]

Next: /exp-discover  (generate hypothesis)
  or: /exp-run "<idea>"  (run directly if you know what to try)
```
