---
story_id: 'US-004'
story_type: 'user_story'
title: 'Instant replay and global stop/replay hotkeys'
epic: '2 Quiet'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 4
---

# US-004: Instant replay and global stop/replay hotkeys

> GitHub issue [#4](https://github.com/lucaschallamel/claude-speak/issues/4) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- `claude-speak again` replays the last clip at once, with no new summary and no new synthesis.
- Document Hyprland keys for stop and replay.

"What did you say?" should take under a second. `/rephrase` stays as the slower "say it differently". The keys work without focusing the terminal.

## Acceptance Criteria

- [ ] **AC1**: Replay starts in under 300 ms.
- [ ] **AC2**: Replay works after the server has been idle, if it is still running.

## Technical Requirements

- `server.py` keeps the last WAV per session, in memory only. Add `POST /replay {session?}`, which defaults to the most recent clip.
- The client gets an `again` subcommand.
- README shows example binds, e.g. `bind = SUPER, Escape, exec, claude-speak stop`. It also shows how to wrap the dictation key as `claude-speak stop; voxtype record start`, which gives barge-in on macOS-style setups with no state file.
- Hotkeys need `claude-speak` on PATH. Document a symlink to the plugin's `bin/claude-speak`.
