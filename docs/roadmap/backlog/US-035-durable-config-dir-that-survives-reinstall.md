---
story_id: 'US-035'
story_type: 'user_story'
title: 'Durable config dir that survives reinstall'
epic: '3 Smarter speech'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-16'
github_issue: 35
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #35, filed by the backlog review of 2026-11-16; status Draft.

# US-035: Durable config dir that survives reinstall

> GitHub issue [#35](https://github.com/lucaschallamel/claude-speak/issues/35) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- Read user settings (`overrides.json`) and user-authored files from `$XDG_CONFIG_HOME/claude-speak/` (default `~/.config/claude-speak/`) first, then the plugin data dir.

A plugin reinstall deletes the data dir, and with it the voice and speed chosen with `/speak-settings`. Planned user files (personas) would be lost the same way, and settings drift across machines.

## Acceptance Criteria

- [ ] **AC1**: After a plugin reinstall, settings chosen with `/speak-settings` are still in effect.
- [ ] **AC2**: Existing installs keep their settings with no migration step; unit tests cover the lookup order.

Effort: S. Could go upstream: yes.

## Technical Requirements

- Writes go to the config dir; reads fall back to the data dir so existing settings keep working.
- Models, caches and markers stay in the data dir.
- The folder can be synced with dotfiles.
