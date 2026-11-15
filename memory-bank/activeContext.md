# Active context

**Last Updated**: 2026-11-15

**Purpose**: the current focus. Rolling: keep the last one or two sessions, move older ones to
[archive/](archive/activeContext-archive.md).

## Current phase

Milestone 2 Quiet: #2 barge-in, #3 hush and #4 replay merged (PRs #20, #21, #23), unreleased.
#5 priority lanes (US-005) is through S7 on `feature/US-005-priority-lanes`; S9 close docs and the
S10 PR are next, then release 0.4.0.

## Session 2026-11-14/15: US-005 , priority lanes (urgent speech preempts chatty speech)

- **Focus**: second story through the full `/cu:pipe`, S0-S8 so far; three S3 rounds, seven fresh
  reviews (S4 x3, S5 x2, S7, plus round-1 S4/S5), two hands-on rounds through `avatar-play`.
- **Delivered**: `/speak` `priority` (urgent, normal, low) and `at`; lanes after any replay;
  another session's higher lane cuts a status line at once and a reply at its next chunk, then the
  reply resumes from its first unplayed chunk; stale status lines (5 s from the hook) dropped by
  the worker and the server; a session's status line never replaces its question or reply; one
  chunk rule for all speech (about 80 chars: sentences, long ones at commas and semicolons);
  stop-ahead plus a single prefetch worker for the waiting question's first chunk; huge or bad
  `at` clamped; CI installs numpy on the 3.13 jobs. 112 tests.
- **Key decisions** (Lucas, 23 in the story file): cut status lines, resume replies; staleness
  from the hook at both ends; fix the cold case in the story (AC6); one ~80-char chunk rule after
  hearing a 15 s wait over a reply; prefetch; AC1 bars are medians, met on a quiet machine
  (decision 23), loaded tail a known limit; offer Quiet features upstream later as a batch.
- **Measured** (quiet machine): status line median 0.74 s / worst 0.80 s; reply 0.00 s after the
  chunk (hands-on 2.0 s wait, was 15 s); cold case median 1.16 s / worst 1.39 s.
- **Learnings**: check machine load before measuring Kokoro (load 13-18 gave 0.7-9.6 s for the same
  code); Kokoro synthesis can't be interrupted, so chunk size bounds how long preempting speech
  waits; listening found the 15 s reply wait that the scripted cases missed; my ponytail review
  missed a drain-thread leak a fresh reviewer found; the avatar page needs a click before it plays.
- **Journal**: [2026-11-15-us-005-priority-lanes](../docs/dev-journal/2026/11/2026-11-15-us-005-priority-lanes.md)

## Next steps

- [/] US-005: S9 close docs (story overview: permission prompts are US-006; AC order), S10 PR
      with the CI matrix green (numpy on 3.13), merge on approval, then the close PR.
- [ ] Release 0.4.0 (brings `again`, the replay key and lanes to installs); laptop update block
      ends the running `server.py` after updating (the old server keeps running without lanes; `claude-speak stop` only stops playback).
- [ ] After 0.4.0: `git fetch upstream`; then agent-avatar #7 (COPPER setup first).
- [ ] Optional: show "in progress" on GitHub at S0 (an issue label), since `main` only shows a
      story's status after its merge.
