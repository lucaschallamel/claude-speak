---
story_id: 'US-007'
story_type: 'user_story'
title: 'Pronounce code identifiers and paths as words'
epic: '4 Smarter speech'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 7
---

> [!note]- Progress updates
>
> - **2026-11-14**: Story file created from GitHub issue #7 (filed 2026-11-07); status Draft.

# US-007: Pronounce code identifiers and paths as words

> GitHub issue [#7](https://github.com/lucaschallamel/claude-speak/issues/7) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

Before speaking, rewrite code-like tokens:
- `claude_speak.py` becomes "claude speak dot py".
- `fooBar` becomes "foo bar".
- `src/a/b.ts` becomes "b dot ts in a".
- `CLAUDE_SPEAK_PLAYER` is read as words.

Short replies and status lines skip the summarizer, so raw identifiers reach Kokoro and come out garbled.

## Acceptance Criteria

- [ ] **AC1**: Unit tests cover each rewrite rule and the prose that must not change.

Depends on the unit test suite story, so the change lands with tests.

Effort: S. Could go upstream: yes.

## Technical Requirements

- Add a `pronounce()` step in `speakable()`: split snake case and camel case, keep the last two path segments, and say dots in file names.
- Users can add their own words in `<data>/lexicon.json`.
- Leave ordinary prose alone ("e.g.", version numbers, URLs).
