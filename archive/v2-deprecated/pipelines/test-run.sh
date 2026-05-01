#!/usr/bin/env bash
# pr-followup pipeline — runs on heartbeat (1h interval).
#
# Reads GitHub notifications and acts on reviewer feedback for existing PRs.
# Never opens new PRs — that's auto-pr's job. Uses opus-4.7 for reasoning
# quality since follow-up decisions are nuanced (yield vs. push vs. wait).

set -euo pipefail

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
LOG_DIR="$HOME/claw/.openclaw/hermes/logs"
LOG_FILE="${LOG_DIR}/pr-followup-${TIMESTAMP}.log"
RESULT_FILE="${LOG_DIR}/pr-followup-${TIMESTAMP}.result"
SESSION_NAME="pr-followup"
LOCK_FILE="/tmp/pr-followup.lock"

mkdir -p "$LOG_DIR"

# Prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
  PID=$(cat "$LOCK_FILE" 2>/dev/null)
  if kill -0 "$PID" 2>/dev/null; then
    echo "[$TIMESTAMP] pr-followup already running (PID $PID), skipping"
    exit 0
  fi
  rm -f "$LOCK_FILE"
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

echo "[$TIMESTAMP] Starting pr-followup pipeline"
echo "  Log: $LOG_FILE"

PROMPT='Execute the pr-followup skill. This is a follow-up run, NOT a new-PR run.

HARD CONSTRAINTS:
1. Do NOT open any new PR.
2. Do NOT claim any new issue.
3. Do NOT create any new fork unless acting on a PR that already exists.
4. If GitHub notifications show no new human (non-bot) activity since last run, exit cleanly with "no actionable items" report.

WHAT TO DO:
1. Read the GitHub inbox via `gh api /notifications`.
2. For each unread item on a PR or issue we authored/commented on:
   a. Classify per pr-followup skill Phase 2 (REQUESTED_CHANGE / APPROVED_WAITING / BLOCKED_PREREQ / COMPETING_CLAIM / MERGED / REJECTED / QUESTION / NO_OP).
   b. Act per Phase 3 for that category.
3. For any COMPETING_CLAIM: close our PR (or step back on the issue) with a graceful yield message. This is the highest priority — do not leave us blocking another contributor.
4. For any REQUESTED_CHANGE: reproduce the ask locally, push the minimal commit, reply succinctly. Use Codex (codex:codex-rescue) for write-mode fixes and Gemini (gemini:gemini-consult) for architecture sanity-checks on changes touching >30 lines.
5. Triple-review every pushed commit per Phase 4 before force-push.

OUTPUTS:
- Write a run summary to ~/workspace/pr-stage/_followup/${TIMESTAMP}.md with sections: Processed, Pushed, Yielded, Waiting, Skipped.
- At the end, print a JSON summary with keys: processed, pushed, yielded, waiting, skipped.

Git identity: 20bytes <133551439+20bytes@users.noreply.github.com>. Push target: the fork, never upstream.'

tmux new-session -d -s "$SESSION_NAME" bash -c "
  export HOME=$HOME
  export PATH=$HOME/.bun/bin:$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin
  export GH_CONFIG_DIR=$HOME/.config/gh
  export GITHUB_TOKEN=\$(gh auth token 2>/dev/null || echo '')
  cd \$HOME

  echo '=== pr-followup started at $(date -u) ===' | tee '$LOG_FILE'

  timeout 2400 $HOME/.bun/bin/claude \
    --dangerously-skip-permissions \
    --model claude-opus-4-7 \
    --verbose \
    --add-dir \$HOME/workspace \
    -p '$PROMPT' \
    2>&1 | tee -a '$LOG_FILE'

  EXIT_CODE=\$?
  END_TS=\$(date -u +'%Y-%m-%dT%H:%M:%SZ')
  echo '' | tee -a '$LOG_FILE'
  echo \"=== pr-followup finished at \$END_TS (exit=\$EXIT_CODE) ===\" | tee -a '$LOG_FILE'

  cat > '$RESULT_FILE' <<EOF
{
  \"pipeline\": \"pr-followup\",
  \"status\": \"\$([ \$EXIT_CODE -eq 0 ] && echo 'DONE' || echo 'FAILED')\",
  \"exit_code\": \$EXIT_CODE,
  \"started_at\": \"$TIMESTAMP\",
  \"finished_at\": \"\$END_TS\",
  \"log_file\": \"$LOG_FILE\"
}
EOF
  echo 'Result written to $RESULT_FILE'
"

echo "tmux session '$SESSION_NAME' launched."
echo "  Attach:  tmux attach -t $SESSION_NAME"
echo "  Tail:    tail -f $LOG_FILE"
