---
story_id: 'US-003'
story_type: 'user_story'
title: 'Hush the session''s speech when a new prompt is submitted'
epic: '2 Quiet'
priority: 'Medium'
story_points: 2
status: 'Done'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 3
---

# US-003: Hush the session's speech when a new prompt is submitted

> GitHub issue [#3](https://github.com/lucaschallamel/claude-speak/issues/3) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

When the user submits a new prompt, stop that session's speech, whether it is queued or playing.

Once you have typed again, the old summary is noise.

## Acceptance Criteria

- [x] **AC1**: Typing a new prompt while the summary plays silences it.
- [x] **AC2**: Other sessions keep talking.

## Technical Requirements

- Add `UserPromptSubmit` to `hooks/hooks.json` with a 2 s timeout.
- In `cmd_hook`, POST `/stop` with `{"session": id}`. The hook must make no `claude -p` call.
- `server.py`: `/stop` with a session drops only that session's queue and its job if it is playing. `/stop` with no body keeps today's behaviour.
