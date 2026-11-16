---
story_id: 'US-036'
story_type: 'user_story'
title: 'Distinct voice per session'
epic: '3 Characters'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-16'
github_issue: 36
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #36, filed by the backlog review of 2026-11-16; status Draft.

# US-036: Distinct voice per session

> GitHub issue [#36](https://github.com/lucaschallamel/claude-speak/issues/36) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- An opt-in setting that gives each session its own voice from a small pool, chosen from the session id, so sessions are told apart by ear.

With several sessions talking, the project name is only spoken when another session spoke in the last 5 minutes. A distinct voice tells sessions apart at once. It covers most of what personas were for, at a fraction of the cost.

## Acceptance Criteria

- [ ] **AC1**: With the setting on, two sessions speak in two different voices, stable across their replies.
- [ ] **AC2**: With it off, behaviour is unchanged; unit tests cover the mapping.

Effort: S. Could go upstream: yes.

## Technical Requirements

- When enabled and no voice was chosen for this session, map a hash of the session id to a voice in a pool of distinct voices of the user's language.
- The user's chosen voice still wins when this is off.
- Added through the settings drift test's four places.
