# Active context archive

**Purpose**: session blocks rolled out of [activeContext.md](../activeContext.md), newest first,
moved verbatim. Not part of the session-start read; consult on demand.

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

## Session 2026-11-14: US-004 , instant replay and global stop/replay hotkeys

- **Focus**: first story through the full `/cu:pipe` (S0-S10); merged as PR #23 (ea64f0a).
- **Delivered**: `claude-speak again`; `POST /replay` that restarts the speech playing now (reusing
  chunks already made) or plays the last stored utterance; the playback loop no longer waits for
  the chunk being synthesised after a cancel (restart 5.3 s -> 0.2 s); double-tap guard, 1 h expiry,
  32-session cap; socket bound `600`; README hotkey wrapper and binds. 78 tests.
- **Key decisions** (Lucas): replay interrupts and keeps the queue; hotkeys via a README wrapper,
  no change to `data_dir()`; mitigate every review finding; release stays per milestone (0.4.0).
- **Learnings**: measure on real hardware (tests were green at 5.3 s); the fork now rewrites
  upstream `Speaker._run` (see systemPatterns "Fork divergences"); COPPER's worktree guard trips on
  any "git" text (even "Github" in a path), so use Edit/Write; the first Orca worktree vanished
  mid-session, recreated as `us-004-instant-replay-2` with no commit lost.
- **Journal**: [2026-11-14-us-004-instant-replay](../docs/dev-journal/2026/11/2026-11-14-us-004-instant-replay.md)

## Session 2026-11-14: COPPER setup

- **Focus**: enable the COPPER harness on this repository.
- **Delivered**: COPPER rules (`.claude/rules/cu/`, user profile filled), pre-push guard, this
  memory bank, `docs/dev-journal/`, `docs/ROADMAP.md`, a Kanban board and one story file per open
  issue in `docs/roadmap/backlog/`.
- **Decisions**: commit COPPER files in the repository; full story files named by GitHub issue
  number (`US-002` = issue #2); the GitHub issue stays the tracker, the story file holds the spec.

## Session 2026-11-13: #2 and #3

- **Delivered**: the server polls the dictation state file every 100 ms and stops speech when it
  leaves `idle` (`CLAUDE_SPEAK_DICTATION_STATE`, voxtype default). `UserPromptSubmit` posts `/stop`
  with the session id and touches `hush-<session>`, so a summary still being written is dropped.
- **Learnings**: an empty state-file read is a half-done write, not idle (double stop on macOS CI).
  `gh pr create` in a fork targets upstream: always pass `--repo lucaschallamel/claude-speak`.

## Session 2026-11-19/20: US-030 , restart a stale server after a plugin update

- **Focus**: third story through the full `/cu:pipe` (standard profile), S0-S10, merged as PR #40 (5eaabfa), in the
  Orca worktree `us-030-stale-server-restart`. Three fresh reviews (S4, S5, S7), one ponytail
  review, and a real-hardware run with scratch plugin copies at five versions.
- **Delivered**: both processes read `version` from `plugin.json`, and `/health` reports
  `version` and `quitting`. The client replaces only an older server: it posts `/quit` under
  `server.lock` and waits up to 120 s (gone = two health misses in a row). A quitting server
  refuses `/speak`, `/replay`, `/warm` and `/synth` with 503, finishes its queue, and exits; after
  `DRAIN_CAP` (100 s) it stops its speech and exits anyway. A 503 is retried once. On exit, the
  socket is removed only if it is still the server's own. `status` shows both versions. 142 tests.
- **Key decisions**: old servers (0.4.x) get no automatic kill; the 0.5.0 update block keeps
  `pkill` once (Lucas, S1). Newer wins. Drain, then refuse. The 120 s wait drops one utterance
  past it. Every review finding was mitigated at Lucas's request ("mitigate all").
- **Learnings**: nest the bounds (server drain cap under client wait); fresh reviewers find race
  windows the author misses; brief read-only reviewers with the exact forbidden git commands; the
  worktree guard refuses git-like text in complex commands, so use Write/Edit or script files.
- **Journal**: [2026-11-20-us-030-stale-server-restart](../docs/dev-journal/2026/11/2026-11-20-us-030-stale-server-restart.md)
