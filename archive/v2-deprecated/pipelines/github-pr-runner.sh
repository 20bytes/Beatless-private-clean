#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
LOG_DIR="$HOME/.hermes/shared/logs"
LOG_FILE="${LOG_DIR}/github-pr-${TIMESTAMP}.log"
SESSION_NAME="github-pr"

mkdir -p "$LOG_DIR"
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

echo "[$TIMESTAMP] Starting github-pr v7 pipeline (chain verification)"
echo "  Log: $LOG_FILE"
echo "  Monitor: tmux attach -t $SESSION_NAME"

PROMPT='Execute the github-pr skill. This is a TRIAL RUN (do NOT submit any PR).

MANDATORY CHAIN VERIFICATION — every link below MUST fire or the trial FAILS:

1. PLANNING-WITH-FILES: Create task_plan.md, findings.md, progress.md in ~/workspace/pr-stage/<repo-name>/. Update them at EVERY phase transition.

2. ISSUE SELECTION (hard gates):
   - Issue must be >7 days old (check createdAt)
   - Must have a HUMAN maintainer comment (authorAssociation = MEMBER/COLLABORATOR/OWNER, NOT a bot like Dosu)
   - No one has asked "assign me" or "I will work on this" in comments
   - No competing PRs exist (check with gh pr list --search)
   - Not filed by 20bytes

3. GEMINI AGENT: Spawn gemini:gemini-consult for repo evaluation (Phase 2). Record what Gemini returned in findings.md.

4. CODEX AGENT: Spawn codex:codex-rescue for fix implementation (Phase 7). Record what Codex changed in findings.md.

5. ROLE SEPARATION IN REVIEW: The agent that implemented the fix (Codex in Phase 7) must NOT review its own code for correctness. Assign Codex to architecture/social review, Gemini to correctness/code quality review. Record which agent reviewed which dimension.

6. SCORING DISCIPLINE: Every score must include file:line references, deduction reasons for <10, and anchor at 7=acceptable. No score of 9-10 without exceptional justification.

7. DYNAMIC VERIFICATION: Bug must be reproduced by running code. Fix must be verified by running tests.

Search for issues in agent/LLM repos with good-first-issue or help-wanted labels. Clone to ~/workspace/contrib/. Save full results to ~/workspace/pr-stage/<repo-name>/pr-report.md.

At the END of the report, add a CHAIN VERIFICATION section listing each of the 7 links above with PASS/FAIL and evidence (timestamp, agent name, file path).'

tmux new-session -d -s "$SESSION_NAME" bash -c "
  echo '=== github-pr v7 pipeline started at $(date -u) ===' | tee '$LOG_FILE'

  timeout 3600 claude \
    --dangerously-skip-permissions \
    --verbose \
    --add-dir $HOME/workspace \
    -p '$PROMPT' \
    2>&1 | tee -a '$LOG_FILE'

  EXIT_CODE=\$?
  END_TS=\$(date -u +'%Y-%m-%dT%H:%M:%SZ')
  echo \"=== Pipeline finished at \$END_TS (exit=\$EXIT_CODE) ===\" | tee -a '$LOG_FILE'
"

echo "tmux session '$SESSION_NAME' launched."
echo "  Attach:  tmux attach -t $SESSION_NAME"
echo "  Tail:    tail -f $LOG_FILE"
