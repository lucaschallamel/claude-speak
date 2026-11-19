---
story_id: 'US-030'
story_type: 'user_story'
title: 'Restart a stale server after a plugin update'
epic: '3 Smarter speech'
priority: 'High'
story_points: 3
status: 'In Progress'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-19'
github_issue: 30
---

> [!note]- Progress updates
>
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

- [ ] **AC1**: From 0.5.0 onwards, after a version bump the next speech runs the new server code with no manual step. A server older than this story (0.4.x and before) still needs the `pkill` line of the update block, one last time.
- [ ] **AC2**: Speech playing or queued when the update is detected finishes before the old server exits.
- [ ] **AC3**: Unit tests cover the version check and `/quit` on a busy and an idle server.
- [ ] **AC4**: A client never restarts a server of the same or a newer version, so two sessions on different plugin versions do not restart each other's server in turn.

Effort: S. Could go upstream: yes.

## Technical Requirements

- The server reads `version` from `.claude-plugin/plugin.json` at start and returns it from `/health`.
- A new `/quit` endpoint makes the server exit once its queue is empty and nothing plays. It never cuts speech in progress.
- `/health` returns `version`. The client restarts the server only when that version is lower than its own (dotted numeric compare). A missing version counts as lower. A server that refuses `/quit` (older than this story) is used as it is, at once, with no wait.
- While quitting, the server answers `/speak` and `/replay` with 503, so a chatty old client cannot keep it alive. It exits within about a second of its queue emptying, not at the next 15 s idle tick.
- The client waits up to 120 s for the old server to go. Past that it logs the problem and drops that one utterance (the quitting server refuses it); the next speech tries again.
- `claude-speak status` prints the server's version.

## Decisions (S1, 2026-11-19)

1. **Old servers (Lucas):** no automatic kill for servers from before this story. The 0.5.0 update block keeps the `pkill` line one last time. Reason: smallest change, no signal-sending code, no platform-specific process lookup.
2. **Newer wins:** restart only an older server; an older client uses a newer server, because the API only grows. Reason: two sessions on different versions would otherwise restart each other forever.
3. **Drain, then refuse:** a quitting server finishes what it has queued and answers new speech with 503. Speech from an old client during the drain is lost and logged.
4. **Wait bound:** 120 s, then log and drop that one utterance; the next speech tries again. Workers are detached, so the wait is not visible. (Corrected at S2: a quitting server refuses new speech, so "speak through the old server" could not work.)

S1 artefact: [US-030-s1-kickoff.md](../pipeline-audit-trail/artifacts/US-030-s1-kickoff.md).
