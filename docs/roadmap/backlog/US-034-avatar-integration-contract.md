---
story_id: 'US-034'
story_type: 'user_story'
title: 'Avatar integration contract: what each player run carries'
epic: '4 Characters'
priority: 'Medium'
story_points: 3
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-16'
github_issue: 34
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #34, filed by the backlog review of 2026-11-16; status Draft.

# US-034: Avatar integration contract: what each player run carries

> GitHub issue [#34](https://github.com/lucaschallamel/claude-speak/issues/34) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- One written contract (`docs/avatar-interface.md`) for what claude-speak gives an avatar player: per run and through `/cue`.
- The server passes an explicit environment to each player run: utterance id, chunk `i/n`, session, mood, gesture, persona, the chunk text, lead-in in ms, and `kind` (`warm` or `speech`).

The server runs the player once per ~80-character chunk, plus warm-up silence runs, and it inherits the environment of whichever session started it. A mood or gesture set per run would fire once per chunk, captions would arrive as fragments, and a persona read from the server's own environment would belong to the first session. Several avatar features (cues tied to their clip, persona channels, captions) depend on this.

## Acceptance Criteria

- [ ] **AC1**: A fake player in the tests receives the documented fields, once per chunk, with the same utterance id across a resume.
- [ ] **AC2**: Warm-up runs are marked `warm` and carry no cue.
- [ ] **AC3**: The contract is documented in the repository.

Effort: M. Could go upstream: partly.

## Technical Requirements

- `Speaker._spawn` builds the env from a base with every `CLAUDE_SPEAK_*` removed, plus the fields above; `_resumed` keeps the utterance id.
- For spoken replies, mood and gesture travel in the `/speak` body with the text, and apply once per utterance; `/cue` stays for cues without audio.
- Generic: no avatar-specific code beyond passing documented fields.
