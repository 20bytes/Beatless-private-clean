# Changelog

This private Beatless repository is a clean Git repository without upstream
author history. The entries below summarize the project changes preserved in
this version.

## Current Private Version

- Added dual-repository operating model: public-facing Beatless materials are
  kept separate from private automation/runtime configuration.
- Reworked the public README with a concise framework overview, architecture
  diagram, quick-start commands, dashboard notes, public-repo safety guidance,
  and a Star History chart.
- Added automation preflight and shared runtime configuration through
  `hermes-scripts/preflight.py` and `hermes-scripts/beatless_config.py`.
- Added GitHub response and PR discovery dry-run support for safe local checks
  before waking Claude Code execution.
- Added Zotero collection inspection, write-probe utilities, and paper-harvest
  helpers for OpenReview, CVF, arXiv, Zotero, and Obsidian workflows.
- Updated experiment commands for `/exp-status`, `/exp-discover`, `/exp-run`,
  and `/exp-review`, including smoke-workspace halt guards, resume handling,
  integration readiness checks, and Codex/Gemini fallback paths.
- Added Claude Code agent bridges for local Codex CLI and Gemini CLI under
  `commands/agents/`.
- Added a FastAPI + Vite dashboard with SSE updates for agents, pipelines,
  experiments, GPU/system status, and recent activity.
- Preserved architecture, pipeline, standard, plan, and archive materials as
  repository content while excluding local secrets, dependency directories,
  build outputs, and machine-specific configuration.

