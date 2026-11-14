---
story_id: 'US-006'
story_type: 'user_story'
title: 'Speak permission prompts and alert the avatar'
epic: '4 Smarter speech'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 6
---

> [!note]- Progress updates
>
> - **2026-11-14**: Story file created from GitHub issue #6 (filed 2026-11-07); status Draft.

# US-006: Speak permission prompts and alert the avatar

> GitHub issue [#6](https://github.com/lucaschallamel/claude-speak/issues/6) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

When Claude waits for permission, say so aloud, e.g. "Claude wants to run a Bash command, approve?". The avatar also shows an attention state.

Permission prompts are where hands-free use stalls. Nothing tells you today.

## Acceptance Criteria

- [ ] **AC1**: A permission prompt is heard within about 1 s of the notification.
- [ ] **AC2**: Nothing is spoken when the session is headless.

## Technical Requirements

- Add a `Notification` hook. When `notification_type` is `permission_prompt`, speak `message` directly, with no summary call so it stays fast, at the highest priority (see priority lanes).
- An `idle_prompt` setting, off by default.
- Send an attention cue, e.g. `[fear handup]`, to `CLAUDE_SPEAK_AVATAR_URL`. The avatar side (eye contact, highlighted border until answered) is a matching story in the avatar repo. The next `UserPromptSubmit` or tool event clears it.

## Check first

The `Notification` payload fields for the installed Claude Code version.

## Settled decisions (from the issue thread)

**2026-11-07**:

Decisions (2026-11-07):
- Speak `permission_prompt`, `elicitation_dialog` and `agent_needs_input` through the `Notification` hook, which can't block or approve anything.
- `idle_prompt` is a setting, off by default.
- No voice approval. `PermissionRequest` exists and can allow or deny, but it stays out of scope for security.
