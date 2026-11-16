---
story_id: 'US-031'
story_type: 'user_story'
title: 'Settings drift test'
epic: '3 Smarter speech'
priority: 'High'
story_points: 1
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-16'
github_issue: 31
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #31, filed by the backlog review of 2026-11-16; status Draft.

# US-031: Settings drift test

> GitHub issue [#31](https://github.com/lucaschallamel/claude-speak/issues/31) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- A unit test that fails when a setting is added in one place but not the others.

CLAUDE.md requires every new setting in `DEFAULTS`, `plugin.json` `userConfig`, `OVERRIDABLE` (if user-toggleable) and the `speak-settings` skill. Nothing enforces it, and the next stories add settings.

## Acceptance Criteria

- [ ] **AC1**: The test passes on main and fails when a setting is added to only one of those places.

Effort: XS. Could go upstream: yes.

## Technical Requirements

- `set(DEFAULTS) == set(userConfig)` (both hold `auto_speak`, `speed`, `summarize`, `summary_model`, `voice` today).
- `OVERRIDABLE` is a subset of `DEFAULTS`.
- Every `OVERRIDABLE` key is named in `skills/speak-settings/SKILL.md`.
