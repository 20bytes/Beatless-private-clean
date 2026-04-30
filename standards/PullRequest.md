# Pull Request Quality Gate — 8-Item Standard

Structured for triple-review scoring (Claude + Codex + Gemini).
Each reviewer scores every item 0-10 independently. Final score = average of three reviewers.

**Pass threshold**: minimum 7.0/10.0 overall average.
**Hard-fail items**: Items 1 and 2. Score below 6 on either = automatic rejection regardless of total.

---

## Item 1: Direction Alignment (HARD FAIL)

The PR solves a problem the repository actually wants solved.

**Pass criteria**:
- [ ] Linked to an open issue with `good first issue`, `help wanted`, or `bug` label
- [ ] OR maintainer explicitly acknowledged the problem in an issue comment
- [ ] Change aligns with the project's stated roadmap and long-term vision
- [ ] No conflict with existing PRs or ongoing design discussions

**Fail signals**: No linked issue. Unsolicited feature that contradicts project direction. Maintainer previously rejected similar proposals.

---

## Item 2: Repository Rules Compliance (HARD FAIL)

The PR follows the target repository's contribution standards exactly.

**Pass criteria**:
- [ ] Read and followed `CONTRIBUTING.md`, PR template, and code style guide
- [ ] Commit messages match the project's convention (e.g., Conventional Commits, DCO sign-off)
- [ ] Branch naming follows project convention (if specified)
- [ ] CLA/DCO signed if required
- [ ] CI pipeline passes (lint, type check, tests)

**Fail signals**: Ignored PR template. Wrong commit format. Failed CI. Unsigned CLA/DCO when required.

---

## Item 3: Atomic Scope

One PR solves exactly one problem. No drive-by changes.

**Pass criteria**:
- [ ] Single logical change per PR — one bug fix, one feature, or one doc update
- [ ] No unrelated renames, reformats, or refactors bundled in
- [ ] Diff size is proportional to the problem (ideal: 50-200 LOC; flag if >500)
- [ ] Every commit is self-contained and compiles independently

**Fail signals**: Mixed concerns in one PR. Thousands of lines touching unrelated files. "While I was here, I also..." pattern.

---

## Item 4: Complete Description

The PR description gives a reviewer everything needed to understand, verify, and merge.

**Pass criteria**:
- [ ] States the problem and why it matters (the "why", not just the "what")
- [ ] Explains the implementation approach and any alternatives considered
- [ ] Links the related issue using GitHub keywords (`Fixes #123`)
- [ ] Lists what is NOT included (explicit scope boundaries)
- [ ] For UI changes: includes before/after screenshots or recordings

**Fail signals**: Empty description. No linked issue. "See code" as the only explanation. Missing scope boundaries.

---

## Item 5: Verifiability

The change can be independently verified by a maintainer who has never seen it before.

**Pass criteria**:
- [ ] Includes new or updated tests that cover the change
- [ ] For bug fixes: a test that fails before the fix and passes after
- [ ] Reproduction steps provided (or link to issue with steps)
- [ ] All existing tests pass without modification (no test-weakening)
- [ ] Benchmark results included if performance-related

**Fail signals**: No tests. Existing tests disabled or loosened. "Works on my machine" without evidence. Bug fix without a regression test.

---

## Item 6: Low-Friction Communication

Interaction with maintainers and reviewers minimizes their effort.

**Pass criteria**:
- [ ] Claimed the issue before starting work (comment or assignment)
- [ ] Responded to every review comment with action or explanation
- [ ] Tone is respectful, concise, and uses the project's language (not your own jargon)
- [ ] No unsolicited pings to maintainers on external channels (Twitter, Slack, DMs)
- [ ] If PR is idle >2 weeks, a single polite bump — no pressure

**Fail signals**: Immediate DM to maintainer after submission. Defensive responses to feedback. Ignoring review comments. Aggressive bumping.

---

## Item 7: Continuous Follow-Through

The PR is maintained from open to merge (or graceful close).

**Pass criteria**:
- [ ] Rebased or merged upstream to resolve conflicts promptly
- [ ] CI failures investigated and fixed within 48 hours
- [ ] Requested changes addressed in follow-up commits (not force-pushed away)
- [ ] Stale conversations resolved or explicitly acknowledged
- [ ] If abandoned, the author closes the PR with an explanation

**Fail signals**: PR left in conflict for weeks. CI red with no response. "I'll get to it" followed by silence.

---

## Item 8: Trust Record Building

The contribution pattern demonstrates reliability and long-term intent.

**Pass criteria**:
- [ ] Contributor has prior successful interactions in the project (issues, reviews, discussions)
- [ ] OR this is an appropriate first contribution (docs, typo, small bug, test addition)
- [ ] No pattern of mass low-quality PRs across unrelated repositories
- [ ] Contribution history shows increasing depth in a focused area

**Fail signals**: First ever PR is a large architectural rewrite. Spray-and-pray across dozens of repos with trivial changes. Account created the same week as the PR.

---

## Social Etiquette Rules

These rules apply to ALL external PRs. Violation of any rule is grounds for rejection.

1. **No internal jargon in external PRs.** Never reference private tooling, agent names, workflow systems, or internal methodology. Speak only in the project's own vocabulary.
2. **PRs should be boring.** The best PR is the one easiest to review, easiest to revert, and easiest to verify. Do not use a PR as a showcase.
3. **Use the project's language, not yours.** Match the repository's coding style, naming conventions, comment language, and communication tone exactly.
4. **Humility over cleverness.** Preferred phrases: "I might be wrong, but...", "If this direction doesn't fit, no problem.", "Happy to adjust." Avoid: "My analysis shows...", "The optimal approach is..."
5. **Never show off tooling.** Do not mention your AI agents, multi-model pipelines, or orchestration systems in any public-facing context.

---

## AI Disclosure Requirement

If AI tools were used in any part of the contribution (code generation, analysis, review, documentation), the contributor MUST:

1. **Disclose AI usage** in the PR description (e.g., "AI-assisted implementation, manually reviewed and tested").
2. **Verify every line** — no unreviewed AI-generated code. Maintainers treat unverified AI code as spam.
3. **Own the output** — AI disclosure does not reduce the contributor's responsibility for correctness, testing, and maintenance.
4. **Remove AI artifacts** — no hallucinated comments, no placeholder text, no "as an AI" phrasing anywhere in the code or docs.

---

## Scoring Summary

| # | Item | Weight | Hard Fail? |
|---|------|--------|------------|
| 1 | Direction Alignment | 10 | YES |
| 2 | Repository Rules Compliance | 10 | YES |
| 3 | Atomic Scope | 10 | no |
| 4 | Complete Description | 10 | no |
| 5 | Verifiability | 10 | no |
| 6 | Low-Friction Communication | 10 | no |
| 7 | Continuous Follow-Through | 10 | no |
| 8 | Trust Record Building | 10 | no |

**Scoring**: 0-10 per item (10 = all pass, 7 = minor gaps, 4 = significant issues, 0 = failure).
Hard reject if Item 1 or 2 < 6 from ANY reviewer. Final = mean of 24 scores (3 reviewers x 8 items). Min 7.0 to pass.

---

## PR Description Template

```markdown
## What

[One sentence: what this PR does.]

## Why

[Why this change is needed. Link to issue: Fixes #NNN]

## How

[Implementation approach. Mention alternatives considered.]

## Scope

- Included: [what is in this PR]
- NOT included: [what is explicitly deferred]

## Verification

- [ ] New/updated tests pass
- [ ] Manual verification steps: [describe]
- [ ] Screenshots (if UI): [attach]

## AI Disclosure

[State whether AI tools were used and in what capacity, or "No AI tools used."]
```

<!-- Sources: GitHub Docs (Contributing, Contributor Guidelines), GitHub Blog (Perfect PR), mention.md, GitHub PR 贡献指南.md -->
