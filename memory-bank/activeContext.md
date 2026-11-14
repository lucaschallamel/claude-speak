# Active context

**Last Updated**: 2026-11-14

**Purpose**: the current focus. Rolling: keep the last one or two sessions, move older ones to
[archive/](archive/activeContext-archive.md).

## Current phase

Milestone 2 Quiet: #2 barge-in and #3 hush merged (2026-11-13); #4 replay and hotkeys built and
through review on branch `feature/US-004-instant-replay` (Orca worktree
`~/orca/workspaces/claude-speak/us-004-instant-replay-2`), pipeline at S8 capture, not pushed yet.
Left: #5 priority lanes, then release 0.4.0.

## Session 2026-11-14: US-004 , instant replay and global stop/replay hotkeys

- **Focus**: first story through the full `/cu:pipe` (S0-S8 so far).
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

## Next steps

- [ ] US-004: S9 close docs, S10 push, PR, CI, merge on Lucas's approval, then the close PR.
- [ ] #5 priority lanes, then release 0.4.0 (brings `again` and the replay key to installs).
- [ ] Add `trust-boundary-paths.json` on main so the S5 trust-boundary check runs.
- [?] Lucas: rename the plugin, or keep the reserved name?
