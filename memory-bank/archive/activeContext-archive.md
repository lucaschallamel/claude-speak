# Active context archive

**Purpose**: session blocks rolled out of [activeContext.md](../activeContext.md), newest first,
moved verbatim. Not part of the session-start read; consult on demand.

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
