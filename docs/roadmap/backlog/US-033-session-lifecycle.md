---
story_id: 'US-033'
story_type: 'user_story'
title: 'Session lifecycle: state registry, SessionEnd cleanup, log rotation'
epic: '4 Smarter speech'
priority: 'High'
story_points: 3
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-16'
github_issue: 33
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #33, filed by the backlog review of 2026-11-16; status Draft.

# US-033: Session lifecycle: state registry, SessionEnd cleanup, log rotation

> GitHub issue [#33](https://github.com/lucaschallamel/claude-speak/issues/33) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- Each session's state (working, waiting, idle), since when, its project label and its terminal pid, kept in `sessions/<id>` (which already holds the transcript path).
- A `SessionEnd` hook removes the session's markers and record.
- Old records and markers are pruned, and `server.log` is rotated.

Several planned features need to know which session is in which state (focus the waiting session, a roll call, the avatar's attention state). The data dir also keeps every `hush-`, `interject-` and `sessions/` file forever, and `server.log` grows without bound.

## Acceptance Criteria

- [ ] **AC1**: After a session ends, its files are gone.
- [ ] **AC2**: Another command can read every live session's state.
- [ ] **AC3**: The data dir and `server.log` stop growing without bound; unit tests cover pruning and rotation.

Effort: M. Could go upstream: yes.

## Technical Requirements

- `cmd_hook` updates the state: working on UserPromptSubmit, waiting on AskUserQuestion and permission prompts, idle on Stop.
- `SessionEnd` deletes `hush-`, `interject-`, `skip-` and `mute-` markers and the record of that session.
- At SessionStart, prune records and markers older than 7 days or whose pid is gone; rename `server.log` to `server.log.1` above 1 MB.
- Keep non-speaking hook paths fast: no extra work on PostToolUse beyond what exists.
