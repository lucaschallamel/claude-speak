---
story_id: 'US-004'
story_type: 'user_story'
title: 'Instant replay and global stop/replay hotkeys'
epic: '2 Quiet'
priority: 'Medium'
story_points: 2
status: 'In Progress'
assignee: 'Claude Code'
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 4
---

> [!note]- Progress updates
>
> - **2026-11-14**: [S1_KICKOFF] Scope refined, ACs sharpened, profile standard. Lucas decided: replay interrupts the current clip and keeps the queue; hotkeys use a README wrapper script. Kickoff: `pipeline-audit-trail/artifacts/US-004-s1-kickoff.md`.
> - **2026-11-14**: [S0_SELECT] Story selected, Orca worktree and branch feature/US-004-instant-replay created, pipeline initiated.

# US-004: Instant replay and global stop/replay hotkeys

> GitHub issue [#4](https://github.com/lucaschallamel/claude-speak/issues/4) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- `claude-speak again` replays the last clip at once, with no new summary and no new synthesis.
- Document Hyprland keys for stop and replay.

"What did you say?" should take under a second. `/rephrase` stays as the slower "say it differently". The keys work without focusing the terminal.

## Acceptance Criteria

- [ ] **AC1**: Replay starts in under 300 ms: it plays the stored chunks with no new summary and no synthesis (unit test: `synth` not called; 300 ms checked by hand on omarchy at S6).
- [ ] **AC2**: Replay works after the server has been idle, if it is still running. If the server is not running, or nothing is stored, `claude-speak again` prints `claude-speak: nothing to replay.` and does not start the server.
- [ ] **AC3**: Replay interrupts the clip playing now and plays first; speech already queued plays after it.
- [ ] **AC4**: Only fully synthesised clips are stored; a replay is never stored. `POST /replay {session?}` defaults to the most recent session's clip.
- [ ] **AC5**: README documents hotkeys: a wrapper script for `~/.local/bin/claude-speak` that picks the newest installed version and sets `CLAUDE_SPEAK_DATA` to the plugin data dir, Hyprland binds for stop and replay, and `claude-speak stop; voxtype record start` as barge-in for setups with no state file.

## Technical Requirements

- `server.py` keeps the last clip per session as chunk samples (no lead-in), in memory only; sessions not heard from in an hour are dropped. Add `POST /replay {session?}`; 404 when nothing is stored.
- The client gets an `again` subcommand (`--session` optional). It never starts the server.
- CLAUDE.md lists `/replay` with the other endpoints.
- The `[mood gesture]` cue is not resent on replay (the client sends cues, not the server).

## Decisions (2026-11-14)

- Replay interrupts the current clip and keeps the queue (Lucas). The interrupted clip is lost, as with a new prompt.
- Hotkeys reach the installed plugin through a README wrapper script, not a change to `data_dir()` (Lucas). Outside Claude Code, `data_dir()` falls back to `~/.local/share/claude-speak`, a different socket, and the installed `bin/` path contains the version.
