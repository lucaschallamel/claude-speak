# Progress

**Last Updated**: 2026-11-20

**Purpose**: what works, what is left, and the history. Details per story are in
[docs/roadmap/backlog/](../docs/roadmap/backlog/).

## Works

- Spoken summaries, `/speak`, `/rephrase`, settings skill, spoken questions, mid-turn
  interjections, `[mood gesture]` avatar cues (fork additions in README).
- Released in v0.4.0 (2026-11-15): barge-in on dictation (#2), hush on new prompt (#3), instant
  replay and hotkeys (#4), priority lanes across sessions (#5, PR #26). Installed on omarchy; the
  laptops need the update block.
- Merged to main (US-030, PR #40, 2026-11-20): a plugin update takes
  effect on the next utterance. The old server drains and exits, then the new one starts; only an
  older server is replaced. Reaches installs with 0.5.0.
- 142 unit tests (9 need numpy: CI runs them on the 3.13 jobs, the 3.10 jobs skip them), CI on
  Linux and macOS.

## Milestones

- [x] 1 Foundation: v0.3.3 (2026-11-07), PRs #17, #18, #19.
- [x] 2 Quiet: v0.4.0 (2026-11-15), PRs #20, #21, #23, #26.
- [ ] 3 Smarter speech, next (release 0.5.0): #30, #31, #6, #9, #32, #7, #33, then #35, #37, #12.
- [ ] 4 Characters, after 3: #34, #36, #13, #16 (agent-avatar Foundation is done).
- Parked: #8, #10, #14. Cut (not planned): #11, #15. Order and reasons: backlog review of
  2026-11-16 in `docs/ROADMAP.md` and each story file.

## Known issues

- `claude plugin validate .` fails on the reserved name `claude-speak` (predates the fork; name
  kept by decision).
- Lanes under heavy CPU load: with several busy sessions the question's worst-case wait over a
  status line can pass 2.5 s (Kokoro synthesis slows); met on a quiet machine (US-005 decision 23).

## Decision log

- 2026-11-20 (grilling after US-030): release stays per milestone (0.5.0 at the end of
  milestone 3, with `pkill` once in its update block). A feature PR's merge approval also covers
  its close PR if that PR only flips status (story, card, ROADMAP, pipeline record, memory-bank
  status lines) with CI green. If code changes after S7, a fresh delta review covers that diff.
  The plugin name `claude-speak` is kept for good. US-030 joins the later upstream batch. The
  handoff check is a manual script (`tests/manual/handoff.sh`). Next story: US-031, lightweight.

- 2026-11-19/20 (US-030): replace only an older server (newer wins); drain, then refuse with 503,
  with one retry through `ensure_server()`; 120 s client wait; 100 s server drain cap; no
  automatic kill of 0.4.x servers, so the 0.5.0 update block keeps `pkill` once (Lucas). Every
  S4, S5, S7 and ponytail finding mitigated at Lucas's request. Details are in the story file and
  on issue #30.

- 2026-11-14 (US-004): replay restarts the speech playing now rather than an older clip; a
  cancelled job stops waiting for synthesis in flight (rewrites upstream `_run`).
- 2026-11-14: release stays per milestone; `again` reaches installs with 0.4.0.
- 2026-11-16 (backlog review: four-seat adversarial council plus a judge): Smarter speech before
  Characters, milestones renamed 3 and 4 to match ("useful first", Lucas's choice over "characters first"); 8 new stories (#30-#37:
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
- 2026-11-19/20: US-030 stale-server restart delivered through the full pipeline (PR #40, 5eaabfa).
