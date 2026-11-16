# Progress

**Last Updated**: 2026-11-16

**Purpose**: what works, what is left, and the history. Details per story are in
[docs/roadmap/backlog/](../docs/roadmap/backlog/).

## Works

- Spoken summaries, `/speak`, `/rephrase`, settings skill, spoken questions, mid-turn
  interjections, `[mood gesture]` avatar cues (fork additions in README).
- Released in v0.4.0 (2026-11-15): barge-in on dictation (#2), hush on new prompt (#3), instant
  replay and hotkeys (#4), priority lanes across sessions (#5, PR #26). Installed on omarchy; the
  laptops need the update block.
- 112 unit tests (9 need numpy: CI runs them on the 3.13 jobs, the 3.10 jobs skip them), CI on
  Linux and macOS.

## Milestones

- [x] 1 Foundation: v0.3.3 (2026-11-07), PRs #17, #18, #19.
- [x] 2 Quiet: v0.4.0 (2026-11-15), PRs #20, #21, #23, #26.
- [ ] 4 Smarter speech, next (release 0.5.0): #30, #31, #6, #9, #32, #7, #33, then #35, #37, #12.
- [ ] 3 Characters, after 4: #34, #36, #13, #16 (agent-avatar Foundation is done).
- Parked: #8, #10, #14. Cut (not planned): #11, #15. Order and reasons: backlog review of
  2026-11-16 in `docs/ROADMAP.md` and each story file.

## Known issues

- `claude plugin validate .` fails on the reserved name `claude-speak` (predates the fork; name
  kept by decision).
- Lanes under heavy CPU load: with several busy sessions the question's worst-case wait over a
  status line can pass 2.5 s (Kokoro synthesis slows); met on a quiet machine (US-005 decision 23).

## Decision log

- 2026-11-14 (US-004): replay restarts the speech playing now rather than an older clip; a
  cancelled job stops waiting for synthesis in flight (rewrites upstream `_run`).
- 2026-11-14: release stays per milestone; `again` reaches installs with 0.4.0.
- 2026-11-16 (backlog review: four-seat adversarial council plus a judge): milestone 4 before
  milestone 3 ("useful first", Lucas's choice over "characters first"); 8 new stories (#30-#37:
  stale-server restart, settings drift test, mute one session, session lifecycle, avatar
  contract, durable config dir, distinct voice per session, focus the waiting session); US-006
  voice-only first; US-007/009/012/013/016 reduced; #8/#10/#14 parked; #11/#15 cut.
- 2026-11-14/15 (US-005): lanes urgent > normal > low after replay; cut status lines, resume
  replies at a chunk boundary; stale status lines dropped 5 s after the hook; one ~80-char chunk
  rule for all speech (was 250) after a 15 s wait was heard over a reply; stop-ahead and a single
  prefetch worker; the latency bars are medians, met on a quiet machine. All 23 decisions are in
  the story file and on issue #5.

## History

- 2026-11-07: CLAUDE.md, tests, CI, table-reading fix; backlog of 15 issues; Serena onboarded.
- 2026-11-13: #2 barge-in and #3 hush merged.
- 2026-11-14: COPPER harness enabled (PR #22); US-004 delivered through the full pipeline (PR #23).
- 2026-11-14: trust-boundary list and workflow decisions on main (PR #25).
- 2026-11-14/15: US-005 priority lanes through S0-S8 on its branch.
