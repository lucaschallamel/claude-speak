---
entry_date: 2026-11-14
author: 'Lucas Challamel'
focus_area: 'US-004 instant replay and global stop/replay hotkeys'
status: completed
session_duration: 'about 4 hours'
tags: [us-004, replay, hotkeys, server, playback-loop, cu-pipe]
version: '1.0.0'
last_updated: '2026-11-14'
maintained_by: 'Lucas Challamel'
---

**Session summary**: US-004 shipped `claude-speak again`, a `/replay` endpoint and README hotkeys
through the full COPPER pipeline, and the reviews turned a naive "replay the stored clip" into a
replay that restarts whatever is playing within 0.2 s.

## Why (High-Level Context)

"What did you say?" should take under a second, from any window. Issue #4 asked for an instant
replay with no new summary or synthesis, and global keys for stop and replay.

**Session objectives**:

- Deliver US-004 as the first story through `/cu:pipe` after the COPPER setup.
- Keep the fork change small enough to merge upstream later.

**Related work**:

- User story: [US-004](../../../roadmap/backlog/US-004-instant-replay-and-global-stop-replay.md)
  (issue #4), milestone 2 Quiet
- Pipeline record: `docs/roadmap/pipeline-audit-trail/US-004.yaml` and its `artifacts/`

## How (The Journey)

### The Initial Problem

The issue said "keep the last WAV". There is no last WAV: `Speaker._run` synthesises each sentence
chunk into its own temp file and deletes it after playing. Hotkeys had a second, hidden problem:
outside Claude Code the client falls back to `~/.local/share/claude-speak`, a different server
socket, and the installed plugin's `bin/` path contains its version, so a plain hotkey would
silently do nothing.

### The Investigation

Kickoff (S1) found both by reading `server.py` and `data_dir()`. Lucas decided: replay interrupts
the current clip and keeps the queue; hotkeys use a README wrapper script that picks the newest
installed version and sets `CLAUDE_SPEAK_DATA`, with no change to `data_dir()`.

### The Breakthrough

The first build stored each utterance's chunk samples once synthesis finished and replayed them.
It met the ACs on paper (84 ms in a real Kokoro run with a logging player), but the S4 author
review found the case that matters most: pressing replay during a long spoken question replayed an
*older* clip and lost the question, because a multi-chunk utterance is not stored until all its
chunks are made. The fix was a definition: the last thing said is the speech playing now.

### Implementation and Refinements

- Replay restarts the current job from the top, reusing `job.made` (chunks already produced) and
  synthesising only the rest. A first version re-synthesised everything: the real run measured
  5.3 s to restart. Reusing made chunks brought it to 2.2 s.
- The remaining 2.2 s was an old behaviour of the playback loop: a cancelled job still waited for
  the chunk being synthesised before the next job could start. The consumer now polls the clip
  queue every 50 ms, returns as soon as its job is cancelled, and a drain thread deletes the
  leftover temp files. Restart: 0.2 s. This also speeds up the speech that follows a barge-in, a
  hush or a newer reply. It rewrites upstream code, so it is recorded under "Fork divergences" in
  `memory-bank/systemPatterns.md`.
- Review rounds added: rate set before a chunk is appended (a replay could see a chunk without its
  rate); storing as soon as the last chunk is made, before a queue put that may wait; skipping a
  current job already cancelled; a double tap ignored within 0.5 s of a replay starting; clips
  expire after an hour; at most 32 sessions kept; the socket bound under umask `0o177` (live
  socket `600`, was `755`); the client treats a server that vanished after the health check as
  "nothing to replay"; the wrapper fails clearly when the plugin is not installed.
- Files: `scripts/server.py`, `scripts/claude_speak.py`, `tests/test_server.py`,
  `tests/test_client.py`, `README.md`, `CLAUDE.md`, `memory-bank/systemPatterns.md`.

### Validation and Documentation

- 78 unit tests (73 run in CI, where numpy is stubbed; 5 need numpy and drive `_run` for real).
  New tests were checked to fail on the previous code by swapping the old `server.py` in.
- A scratchpad script ran the worktree server with real Kokoro and a logging player: 87 ms replay
  of a finished reply, 0.2 s restart mid-speech, all chunks played once.
- Hands-on on omarchy through `avatar-play`: Lucas heard the replay at once with the avatar's mouth
  moving, and the mid-speech restart played once. He bound SUPER+Escape to the wrapper: stop
  works. The replay key waits for 0.4.0 (the installed 0.3.3 has no `again`).
- Coverage (coverage.py, branch): every line US-004 added is covered except `job.started` in the
  loop thread, which unit tests do not run.
- Reviews: fresh subagents at S4 (twice), S5 and S7, each given paths only; Lucas asked for every
  finding to be mitigated at each gate.

## Final State & Next Steps

**State**: branch `feature/US-004-instant-replay` in the Orca worktree
`~/orca/workspaces/claude-speak/us-004-instant-replay-2`, not pushed yet. All ACs met; S8 capture
in progress.

**Next**:

- [ ] S9 close docs, S10 push, PR, CI, merge on Lucas's approval, then the close PR.
- [ ] #5 priority lanes, then release 0.4.0 (brings `again` and the replay key to installs).
- [ ] Follow-up: add `trust-boundary-paths.json` on main so the S5 trust-boundary check runs.

**Knowledge to keep**:

- Measure on real hardware before calling latency done: the unit tests were green at 5.3 s.
- The COPPER in-session guards misread commands: any text containing "git" (even "Github" in a
  path or `github_issue` in YAML) can trip the worktree guard; use Edit/Write or globbed paths.
- The first Orca worktree vanished mid-session for an unknown reason; the branch kept every commit.
  It was recreated as `us-004-instant-replay-2`.

## Reflection

The pipeline was heavy for a 2-point story, but each review round found something real: the lost
question (author), the half-made storage edges (fresh S4 round 2), socket permissions (fresh S5),
and the double tap after start (fresh S7). The biggest win came from measuring, not reviewing: the
5.3 s restart only showed up in the real run.
