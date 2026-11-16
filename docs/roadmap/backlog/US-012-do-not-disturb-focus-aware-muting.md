---
story_id: 'US-012'
story_type: 'user_story'
title: 'Do-not-disturb, focus-aware muting and a ''while you were away'' recap'
epic: '3 Smarter speech'
priority: 'Medium'
story_points: 3
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-16'
github_issue: 12
---

> [!note]- Progress updates
>
> - **2026-11-16**: Backlog review: Reduced. Priority Medium.
> - **2026-11-14**: Story file created from GitHub issue #12 (filed 2026-11-07); status Draft.

# US-012: Do-not-disturb, focus-aware muting and a 'while you were away' recap

> GitHub issue [#12](https://github.com/lucaschallamel/claude-speak/issues/12) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- A DND toggle, e.g. the file `~/.local/state/claude-speak/dnd` toggled by a Hyprland bind or `claude-speak dnd on|off`.
- An optional `speak_when: always|unfocused` setting that stays quiet while the session's terminal has focus.
- Lines held back during DND are logged. When DND ends, one spoken recap covers all sessions.

No speech in meetings. Coming back to one digest beats a stream of stale lines.

## Acceptance Criteria

- [ ] **AC1**: DND silences everything.
- [ ] **AC2**: Ending DND plays one recap.
- [ ] **AC3**: Focus muting can be turned off and is off by default.

## Technical Requirements

- Log every spoken or held line to `<data>/spoken.jsonl`.
- `claude-speak recap` summarizes the entries since the last recap.
- Focus check: on Hyprland, compare `hyprctl activewindow -j` with the terminal pid found by walking up from the hook's parent; on macOS use `osascript`. When the pid walk fails (tmux, SSH), speak.
- Keep the Omarchy-specific triggers, such as the hypridle unlock, out of the core.

## Backlog review (2026-11-16)

- Do-not-disturb already exists: `claude-speak auto off` mutes every session. Deliver a documented hotkey for it, not new code.
- Keep the spoken-lines log and the recap; it is the single history store that the avatar's history panel will read too.
- Cut focus-aware muting (the pid walk to the focused window).
- Keep the log in the data dir (not `~/.local/state`), so `CLAUDE_SPEAK_DATA` isolation still holds.
