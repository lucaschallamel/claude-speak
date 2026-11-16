---
story_id: 'US-030'
story_type: 'user_story'
title: 'Restart a stale server after a plugin update'
epic: '4 Smarter speech'
priority: 'High'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-16'
github_issue: 30
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #30, filed by the backlog review of 2026-11-16; status Draft.

# US-030: Restart a stale server after a plugin update

> GitHub issue [#30](https://github.com/lucaschallamel/claude-speak/issues/30) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- `/health` reports the plugin version the server runs.
- `ensure_server()` compares it with its own version. On a mismatch it asks the old server to exit as soon as nothing is playing or queued, then starts the new one.

After an update the old server keeps running the old code for up to `CLAUDE_SPEAK_IDLE_TIMEOUT` (30 minutes). Today the fix is a manual `pkill` on every machine, every release, and `claude-speak stop` only stops playback.

## Acceptance Criteria

- [ ] **AC1**: After a version bump, the next speech runs the new server code with no manual step.
- [ ] **AC2**: Speech playing when the update is detected finishes before the old server exits.
- [ ] **AC3**: Unit tests cover the version check and `/quit` on a busy and an idle server.

Effort: S. Could go upstream: yes.

## Technical Requirements

- The server reads `version` from `.claude-plugin/plugin.json` at start and returns it from `/health`.
- A new `/quit` endpoint makes the server exit once its queue is empty and nothing plays. It never cuts speech in progress.
- The client restarts the server only when the versions differ. A server with no version (older than this story) counts as stale.
