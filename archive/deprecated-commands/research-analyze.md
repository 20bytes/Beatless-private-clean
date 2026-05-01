---
description: Analyze a research topic from multiple dimensions using Agent Teams. Spawns N teammates each entering from a different dimension (dataset, architecture, loss, training, axiom, cross-domain), invokes Gemini for academic search + devil's advocate and Codex for feasibility. Produces submission-grade A-tier idea spec.
argument-hint: [topic-description]
---

# Research Analyze: A-Tier Idea Generator

Analyze the research topic: **$ARGUMENTS**

## Your Role: Team Lead

You are the LEAD of a research idea generation team. Your goal is to produce a submission-grade A-tier conference idea spec.

---

## Step -1: Problem Value Gate (MANDATORY)

Answer these 4 questions about "$ARGUMENTS". If any is NO, warn the user before proceeding.

| # | Question | YES = Proceed | NO = Reconsider |
|---|----------|--------------|-----------------|
| 1 | Is this a **recognized pain point** in the target community? | Community papers acknowledge this gap | Only you think this matters |
| 2 | Is the pain point **structural** (not just metric optimization)? | Architectural/representational failure | Just "SOTA is 85%, I want 87%" |
| 3 | Does this fit **A-tier venue narrative**? | "This changes how I think about X" | "Nice improvement" |
| 4 | If solved, does it **rewrite understanding** or just add a module? | Framework/paradigm shift | +1 component |

Score 4/4 → strong. 3/4 → proceed with caution. ≤2/4 → suggest reframing.

---

## Step 0: Read Context + Initialize Planning (Lead Only)

Read these files to understand the methodology:
- $HOME/.claude/skills/research-dialectics/references/methodology-summary.md (compact version)
- $HOME/.claude/agents/research-teammate.md (pipeline steps)

Read topic-specific files if they exist in the project working directory. Do NOT read Research_Methodology.md (501 lines) or TwoTopic.md (504 lines) — too expensive. Use the compact summary instead.

**Lead planning initialization** (planning-with-files, lead only — do NOT push to teammates):
Create these files in the project working directory:
- `task_plan.md` — entry dimensions, teammate assignments, round progress
- `findings.md` — teammate verdicts, prior art threats, contradictions, synthesis
- `progress.md` — spawn status, backend type, Gemini/Codex success, reports received

---

## Step 0.5: Topic Refinement (Optional — only if topic is vague)

If the topic description is underspecified (no clear pain point, no venue, no structural claim):
- Use Skill tool to invoke `/superpowers:brainstorming` for scope check, venue fit, and question sharpening
- Refine the topic before proceeding to Step 1
- Update `task_plan.md` with the refined topic

If the topic is already well-specified (has venue, structural claim, prior art awareness) → skip this step.

---

## Step 1: Create Agent Team

Use TeamCreate to create a team for this analysis. Then create tasks for each entry dimension.

---

## Step 2: Select Entry Dimensions

Choose 4-6 entry dimensions. **Mix types** for maximum cognitive diversity:
- 2-3 from decomposition stack layers (Dataset, Architecture, Loss Function, Training Paradigm)
- 1 from abstract axioms (Orthogonality, Duality, Information Bottleneck, etc.)
- 1 from cross-domain analogy (cognitive science, physics, etc.)
- 1 from concrete phenomena (gradient pathology, shortcut learning, etc.)

Record selections in `task_plan.md`.

---

## Step 3: Spawn Teammates

For EACH entry dimension, spawn a teammate using the Agent tool with:
- `team_name`: your team name
- `subagent_type`: `"general-purpose"` (CRITICAL — gives full tool access including Bash, Skill, Agent)
- `name`: descriptive name (e.g., "dataset-analyst", "arch-analyst")
- `mode`: `"bypassPermissions"`

Spawn ALL teammates in PARALLEL (single message with multiple Agent tool calls).

After spawning, update `progress.md` with spawn results (backend type, pane IDs).

---

### Teammate Prompt Template

Each teammate's prompt MUST include ALL of the following:

```
You are a Research Teammate on the "<team-name>" team. Your team lead is "team-lead".

## Assignment
- **Topic**: [full topic description]
- **Entry Dimension**: [assigned dimension]
- **Core Question**: [specific question for this dimension]

## Instructions (follow EVERY step)

1. Read the full pipeline at $HOME/.claude/agents/research-teammate.md — follow Steps 0A through 12 IN ORDER.
2. Read $HOME/.claude/skills/research-dialectics/references/methodology-summary.md for methodology (compact version, saves tokens).
3. Only read topic-specific files in the project working directory if they exist — do NOT read TwoTopic.md or Research_Methodology.md (too long, wastes context).

4. Execute the full pipeline from your assigned entry dimension.

5. Invoke Gemini for academic search + prior art:
   Use Skill tool: /gemini:consult "Search academic literature for: [specific search query]. Return: (1) 5 most relevant papers with titles, venues, years, and one-line summaries, (2) which of these is closest to our approach, (3) what gap remains unfilled."

6. Invoke Gemini for devil's advocate:
   Use Skill tool: /gemini:consult "Play devil's advocate against this research idea: [describe the idea and principle]. Generate the 3 strongest attacks: (1) a simpler explanation for the phenomenon, (2) a prior work that might already solve this, (3) a fundamental flaw in the approach."

7. Invoke Codex for feasibility check:
   Use Skill tool: /codex:rescue "Assess feasibility of this research idea: [describe method]. Check: (1) compute requirements (single A100 budget), (2) implementation complexity, (3) novelty vs closest prior art. Be brutally honest."

8. Write your report to $HOME/research/[project-dir]/teammate_report_[dimension].md

9. Send your verdict to lead:
   SendMessage(to="team-lead", summary="[Dimension] verdict", message="Verdict: [A-Tier/De-Risking/Incremental/Kill] — [2-sentence reasoning]")

## Critical Rules
- Do NOT fabricate citations. If search fails, say "No published evidence found."
- Do NOT skip Gemini or Codex calls. Use the Skill tool (/gemini:consult and /codex:rescue). If they fail or time out, mark as [UNVERIFIED] with the error.
- Kill criteria check at EVERY step. If triggered → STOP immediately with Kill verdict.
- Max 200 words per section in your report.
```

---

## Step 4: Monitor & Coordinate

- Wait for all teammates to report back via SendMessage
- Check task completion status periodically
- If a teammate gets stuck or goes idle for >3 minutes, send guidance via SendMessage
- Update `progress.md` as reports arrive

---

## Step 5: Leader Synthesis

After all reports are in, perform synthesis and record everything in `findings.md`:

### 5A. Convergence Analysis
- Which dimensions arrived at the SAME structural insight?
- Dataset + Architecture convergence → very high confidence
- Axiom + Phenomenon convergence → theoretically + empirically grounded

### 5B. Cross-Layer Contradiction Mining
- WHERE do teammates disagree?
- Contradictions = research opportunities, not failures

### 5C. Prior Art Aggregation
- Union of all closest-3 prior art across teammates
- Multiple teammates flagging same prior art → high threat
- Any principle-level delta found? → that's the best angle

### 5D. Submission-Level Verdict Aggregation
| Teammate Results | Leader Verdict |
|-----------------|---------------|
| 3+ `A-Tier Candidate` | Strong submission candidate → paper drafting |
| Mix of `A-Tier` + `Needs De-Risking` | Conditional → run de-risking experiments first |
| Mostly `Incremental` | Reframe needed → find deeper angle |
| 3+ `Kill` | Abandon or radically reframe |

### 5E. Theory of Mind Simulation
Simulate three minds:
1. **Reviewer 2**: "What would they attack? Which claim is weakest?"
2. **Practitioner**: "What blocks adoption? Is the method practical?"
3. **PhD Student**: "Where would they get stuck extending this?"

### 5F. Comfort Zone Escape Test
"Did I learn something that genuinely SURPRISED me, or did I confirm what I already believed?"

---

## Step 6: Post-Verdict Planning (Lead Only — only if verdict is A-Tier or Conditional A-Tier)

If the synthesis verdict is `A-Tier Candidate` or `Conditional A-Tier`:
- Use Skill tool to invoke `/superpowers:writing-plans` to generate:
  - De-risking experiment plan (MVE → Exp 1-3)
  - Paper structure outline
  - 10-day execution timeline
- Write the plan to `[project-dir]/paper_plan.md`

If the verdict is `Kill` or `Incremental` → skip this step, report to user.

---

## Step 7: Write Synthesis Report

Write the final synthesis to `[project-dir]/leader_synthesis.md`.
Update `findings.md` and `progress.md` with final status.

---

## Step 8: Shutdown Team

After synthesis is complete:
1. Send shutdown request to ALL teammates via SendMessage
2. Wait for shutdown confirmations
3. Verify all teammates terminated
4. Final update to `progress.md`
