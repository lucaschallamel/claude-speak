---
story_id: 'US-016'
story_type: 'user_story'
title: 'Personas: a voice, tone and avatar per session'
epic: '3 Characters'
priority: 'Medium'
story_points: 3
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 16
---

> [!note]- Progress updates
>
> - **2026-11-14**: Story file created from GitHub issue #16 (filed 2026-11-07); status Draft.

# US-016: Personas: a voice, tone and avatar per session

> GitHub issue [#16](https://github.com/lucaschallamel/claude-speak/issues/16) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

A **persona** is a named bundle: voice or blend, speed, summary tone and an avatar ID. Each session speaks as one persona.

```json
{"matilda": {"voice": "bf_emma", "speed": 1.15, "tone": "brisk, dry humour", "avatar": "matilda"}}
```

Today the voice is global: `/speak-settings` writes one `overrides.json` for every session. Saved overrides also outrank environment variables, so a per-project env setting can't change the voice either. With several sessions running you can't tell agents apart except by the spoken project name.

## Acceptance Criteria

- [ ] **AC1**: Two sessions with different personas are heard in different voices.
- [ ] **AC2**: Their clips reach different avatar windows (the avatar repo's persona channels).
- [ ] **AC3**: Sessions with no persona behave exactly as today.

## Technical Requirements

- Personas live in `<data>/personas.json`.
- Choosing the session's persona, highest priority first:
  1. `/speak-persona <name>` for this session, stored per session id.
  2. `CLAUDE_SPEAK_PERSONA` from the project's settings `env`.
  3. Auto-assign: the first persona from the pool that no live session is using, so 3 sessions get 3 different personas.
  4. None: today's global settings.
- A persona's voice and speed override the global settings for that session only. Its `tone` adds one line to `SUMMARY_PROMPT`.
- Every speak job and cue carries `persona` (and the avatar ID). The server passes it to `CLAUDE_SPEAK_PLAYER`, e.g. as env `CLAUDE_SPEAK_PERSONA`, so the player can route the clip to the right avatar window.
- Speech from all sessions still takes turns, so voices never overlap.

## Check first

Whether a project's `.claude/settings.json` `env` reaches plugin hook processes.

Builds on #13 (voice switcher) and #14 (voice blends).

## Settled decisions (from the issue thread)

**2026-11-07**:

Decisions (2026-11-07):
- One shared `personas.json` in claude-speak's data dir holds both the voice side and the avatar side. The avatar repo reads its fields from it (path configurable).
- Ship 4 starter personas: Quad + `bm_george`, julia + `bf_emma`, david + `am_michael`, brunette + `af_heart`, each with a tone line.
- Sessions with no persona get a free one automatically whenever any are defined. With none defined, behaviour is as today.
- `server.py` passes the persona, mood and gesture to the player as environment variables on each run (`CLAUDE_SPEAK_PERSONA`, `CLAUDE_SPEAK_MOOD`, `CLAUDE_SPEAK_GESTURE`). Players that don't know them ignore them.
- Verified: user-level settings `env` reaches plugin hook processes. Project-level `env` is documented but still to be confirmed (docs: it applies after the folder is trusted).
