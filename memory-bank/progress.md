# Progress

**Last Updated**: 2026-11-14

**Purpose**: what works, what is left, and the history. Details per story are in
[docs/roadmap/backlog/](../docs/roadmap/backlog/).

## Works

- Spoken summaries, `/speak`, `/rephrase`, settings skill, spoken questions, mid-turn
  interjections, `[mood gesture]` avatar cues (fork additions in README).
- Barge-in on dictation (#2) and hush on new prompt (#3), merged, not yet released.
- Instant replay (`claude-speak again`, `/replay`) and hotkey docs (#4), merged (PR #23), not yet released.
- 78 unit tests (73 in CI, 5 need numpy), CI on Linux and macOS.

## Milestones

- [x] 1 Foundation: v0.3.3 (2026-11-07), PRs #17, #18, #19.
- [/] 2 Quiet: #2, #3 and #4 done (PRs #20, #21, #23); #5 left. Release 0.4.0.
- [ ] 3 Characters: #13, #14, #16. Needs agent-avatar's Foundation story first.
- [ ] 4 Smarter speech: #6–#12, #15 (SP-015 time box 2 days, decide before milestone 4).

## Known issues

- `claude plugin validate .` fails on the reserved name `claude-speak` (predates the fork).
- No `trust-boundary-paths.json` yet, so COPPER's S5 path check does not run.

## Decision log

- 2026-11-14 (US-004): replay restarts the speech playing now rather than an older clip; a
  cancelled job stops waiting for synthesis in flight (rewrites upstream `_run`).
- 2026-11-14: release stays per milestone; `again` reaches installs with 0.4.0.

## History

- 2026-11-07: CLAUDE.md, tests, CI, table-reading fix; backlog of 15 issues; Serena onboarded.
- 2026-11-13: #2 barge-in and #3 hush merged.
- 2026-11-14: COPPER harness enabled (PR #22); US-004 delivered through the full pipeline (PR #23).
