---
story_id: 'US-005'
story_type: 'user_story'
title: 'Priority lanes: urgent speech preempts chatty speech'
epic: '2 Quiet'
priority: 'Medium'
story_points: 3
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 5
---

> [!note]- Progress updates
>
> - **2026-11-14**: Story file created from GitHub issue #5 (filed 2026-11-07); status Draft.

# US-005: Priority lanes: urgent speech preempts chatty speech

> GitHub issue [#5](https://github.com/lucaschallamel/claude-speak/issues/5) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

Rank speech by priority: permission prompt or question, then the Stop summary, then mid-turn status lines.

A question or a permission request must not wait behind a status line. A status line that is no longer current is not worth hearing.

## Acceptance Criteria

- [ ] **AC1**: With a status line playing, an AskUserQuestion prompt is heard within one chunk.
- [ ] **AC2**: Stale status lines are never spoken.

## Technical Requirements

- Add a `priority` field to `/speak`. The client sets it per hook event.
- `server.py` sorts the queue. A higher-priority job preempts the current one at the next chunk boundary from `split_chunks`, not mid-word.
- Drop status-line jobs older than about 5 s.
