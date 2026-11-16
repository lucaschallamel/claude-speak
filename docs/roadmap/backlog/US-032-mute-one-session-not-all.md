---
story_id: 'US-032'
story_type: 'user_story'
title: 'Mute one session, not all'
epic: '4 Smarter speech'
priority: 'High'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-16'
github_issue: 32
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #32, filed by the backlog review of 2026-11-16; status Draft.

# US-032: Mute one session, not all

> GitHub issue [#32](https://github.com/lucaschallamel/claude-speak/issues/32) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- `/speak-mute [on|off]` mutes or unmutes the current session only.
- Questions and permission prompts (`urgent`) are still spoken.

`/speak-auto off` writes the global `overrides.json`, so silencing one chatty long-running session silences every session.

## Acceptance Criteria

- [ ] **AC1**: A muted session stays silent for replies and status lines while other sessions speak.
- [ ] **AC2**: A question from a muted session is still spoken.
- [ ] **AC3**: Unmuting restores speech; unit tests cover the gate.

Effort: S. Could go upstream: yes.

## Technical Requirements

- A `mute-<session>` marker in the data dir, the same pattern as `hush-` and `skip-`.
- `cmd_hook` skips Stop replies and status lines for a muted session; `urgent` speech goes through.
- A thin `skills/speak-mute/SKILL.md` like the other skills.
