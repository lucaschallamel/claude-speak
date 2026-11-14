---
story_id: 'US-002'
story_type: 'user_story'
title: 'Barge-in: stop speaking when dictation starts'
epic: '2 Quiet'
priority: 'Medium'
story_points: 2
status: 'Done'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 2
---

> [!note]- Progress updates
>
> - **2026-11-14**: Story file created from GitHub issue #2 (filed 2026-11-07), already delivered and closed on GitHub.

# US-002: Barge-in: stop speaking when dictation starts

> GitHub issue [#2](https://github.com/lucaschallamel/claude-speak/issues/2) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

Speech stops the moment the user starts dictating, so Claude never talks over them.

Talking over each other breaks the voice-partner feel. On Omarchy, dictation is push-to-talk with `voxtype`.

## Acceptance Criteria

- [x] **AC1**: Pressing the dictation key cuts speech within about 200 ms.
- [x] **AC2**: The avatar's mouth stops too, through the existing `stop` path in avatar-play.
- [x] **AC3**: With no state file, nothing changes.

## Technical Requirements

- `server.py` gets a watcher thread on voxtype's state file. With `state_file = "auto"` in `~/.config/voxtype/config.toml`, that file is `$XDG_RUNTIME_DIR/voxtype/state`. It reads `idle` when idle.
- When the state becomes `recording`, call the existing stop path, which clears the queue and kills the player.
- Use a 100 ms poll or inotify through ctypes, so the server needs no new dependency.
- The path comes from `CLAUDE_SPEAK_DICTATION_STATE`, with the voxtype default as fallback. With no file, no watcher.
- macOS has no voxtype. There, the hotkey wrapper in the replay story covers it.

## Check first

Every value voxtype writes (`voxtype status --format json`).

## Settled decisions (from the issue thread)

**2026-11-07**:

Decision (2026-11-07): stop on **any state other than `idle`**. Only `idle` has been seen; the binary hints at `recording` and `transcribing`, so we don't rely on exact names.
