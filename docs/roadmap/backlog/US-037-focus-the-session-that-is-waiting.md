---
story_id: 'US-037'
story_type: 'user_story'
title: 'Focus the session that is waiting'
epic: '3 Smarter speech'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-16'
github_issue: 37
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #37, filed by the backlog review of 2026-11-16; status Draft.

# US-037: Focus the session that is waiting

> GitHub issue [#37](https://github.com/lucaschallamel/claude-speak/issues/37) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- `claude-speak focus` focuses the terminal of the session that most recently asked a question or a permission.
- A README hotkey binding next to stop and replay.

Hearing a question from one of several sessions still means hunting for its window before dictating the answer.

## Acceptance Criteria

- [ ] **AC1**: On Omarchy, the hotkey focuses the terminal of the waiting session.
- [ ] **AC2**: With no waiting session it says so; on other platforms it is a harmless no-op.

Effort: S. Could go upstream: no (Hyprland).

## Technical Requirements

- Uses the session state registry (session lifecycle story) for the waiting session and its terminal pid.
- On Hyprland: `hyprctl dispatch focuswindow pid:<terminal>`. Elsewhere, or under tmux or ssh: print what it found and do nothing.
- Never approves anything: it only moves focus.
