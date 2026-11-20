---
story_id: 'US-030'
story_type: 'user_story'
title: 'Restart a stale server after a plugin update'
epic: '3 Smarter speech'
priority: 'High'
story_points: 3
status: 'Done'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-20'
github_issue: 30
---

> [!note]- Progress updates
>
> - **2026-11-20**: [S10_MERGE] PR #40 squash-merged as 5eaabfa on Lucas's approval (CI 4/4 green on e278c35); issue #30 closed; story Done, card DONE, pipeline completed.
> - **2026-11-20**: [S9_CLOSE] AC1-AC4 ticked as met (AC1 and AC2 on real hardware at S6, AC3 by 142 unit tests, AC4 in tests and on hardware); close docs committed; status stays In Progress until the merge.
> - **2026-11-20**: [S8_CAPTURE] Dev journal written; memory bank updated (US-005 session block archived); README restart bullet reworded so it no longer contradicts the 100 s cap.
> - **2026-11-20**: [S7_CRITICAL_REVIEW] Fresh DoD review WARN (all ACs pass, no FAIL), 6 findings; Lucas asked for all to be mitigated: story spec brought in line (AC2 drain cap, 503 list, decision 3), server docstring, say --out retries a 503, status and retry tests, release step for a real update check; 142 tests pass.
> - **2026-11-20**: [S5_ARCH_SEC_COMP_REVIEW] Fresh review PASS, 9 findings (3 Low, 6 Info), trust boundary touched, not security-sensitive; Lucas asked for all to be mitigated: server drain cap, /synth refused and held, own-socket removal, waiting notice, marker cleanup, dev data-dir note; 140 tests pass.
> - **2026-11-19**: [S4_CODE_REVIEW] Fresh review PASS, 9 findings (5 Low, 4 Info); Lucas asked for all to be mitigated: 7 fixed in code and tests (134 pass), 2 handled by docs and the release checklist.
> - **2026-11-19**: [S3_EXECUTE] Server reports its version, /quit drains then exits, 503 while quitting; client replaces only an older server; status shows the version; 14 new tests (126 pass); README and CLAUDE.md updated.
> - **2026-11-19**: [S1_KICKOFF] Scope refined: restart only an older server, drain then exit, 503 while quitting, 120 s wait; old servers need one last manual step (Lucas); ACs 3 -> 4; points 2 -> 3; profile standard.
> - **2026-11-19**: [S0_SELECT] Story selected, Orca worktree and branch feature/US-030-stale-server-restart created, pipeline initiated; status In Progress.
> - **2026-11-16**: Story file created from GitHub issue #30, filed by the backlog review of 2026-11-16; status Draft.

# US-030: Restart a stale server after a plugin update

> GitHub issue [#30](https://github.com/lucaschallamel/claude-speak/issues/30) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- `/health` reports the plugin version the server runs.
- `ensure_server()` compares it with its own version. On a mismatch it asks the old server to exit as soon as nothing is playing or queued, then starts the new one.

After an update the old server keeps running the old code for up to `CLAUDE_SPEAK_IDLE_TIMEOUT` (30 minutes). Today the fix is a manual `pkill` on every machine, every release, and `claude-speak stop` only stops playback.

## Acceptance Criteria

- [x] **AC1**: From 0.5.0 onwards, after a version bump the next speech runs the new server code with no manual step. A server older than this story (0.4.x and before) still needs the `pkill` line of the update block, one last time.
- [x] **AC2**: Speech playing or queued when the update is detected finishes before the old server exits. Only a drain longer than 100 s (a hung player) is cut, so the old server cannot outlive the client's 120 s wait (S5 finding 2).
- [x] **AC3**: Unit tests cover the version check and `/quit` on a busy and an idle server.
- [x] **AC4**: A client never restarts a server of the same or a newer version, so two sessions on different plugin versions do not restart each other's server in turn.

Effort: S. Could go upstream: yes.

## Technical Requirements

- The server reads `version` from `.claude-plugin/plugin.json` at start and returns it from `/health`.
- A new `/quit` endpoint makes the server exit once its queue is empty, nothing plays and no `/synth` reply is being written. It does not cut speech in progress, except after `DRAIN_CAP` (100 s, below the client's 120 s wait): then it stops its speech and exits, so a hung player cannot keep it alive.
- `/health` returns `version`. The client restarts the server only when that version is lower than its own (dotted numeric compare). A missing version counts as lower. A server that refuses `/quit` (older than this story) is used as it is, at once, with no wait.
- While quitting, the server answers `/speak`, `/replay`, `/warm` and `/synth` with 503, so a chatty old client cannot keep it alive. It exits within about a second of its queue emptying, not at the next 15 s idle tick.
- The client waits up to 120 s for the old server to go. Past that it logs the problem and drops that one utterance (the quitting server refuses it); the next speech tries again.
- `claude-speak status` prints the server's version.

## Decisions (S1, 2026-11-19)

1. **Old servers (Lucas):** no automatic kill for servers from before this story. The 0.5.0 update block keeps the `pkill` line one last time. Reason: smallest change, no signal-sending code, no platform-specific process lookup.
2. **Newer wins:** restart only an older server; an older client uses a newer server, because the API only grows. Reason: two sessions on different versions would otherwise restart each other forever.
3. **Drain, then refuse:** a quitting server finishes what it has queued and answers new speech with 503. A client retries a 503 once through `ensure_server()`, which waits for the old server and starts the new one; only a second 503 is lost and logged. (Updated at S4 and S5: the single retry, and the 100 s drain cap.)
4. **Wait bound:** 120 s, then log and drop that one utterance; the next speech tries again. Workers are detached, so the wait is not visible. (Corrected at S2: a quitting server refuses new speech, so "speak through the old server" could not work.)

## Release

- Release 0.5.0 must bump `.claude-plugin/plugin.json` to `0.5.0`: AC1 starts with that version, and the `status` text calls an unversioned server "older than 0.5.0".
- The 0.5.0 update block keeps the `pkill` line once, for the 0.4.x server (S1 decision 1).
- After installing 0.5.0 and later 0.5.x, run `claude-speak status` once to see the server version change with no manual step. This repeats the S6 hardware check on a real `claude plugin update` (S7 finding F5).

S1 artefact: [US-030-s1-kickoff.md](../pipeline-audit-trail/artifacts/US-030-s1-kickoff.md).
