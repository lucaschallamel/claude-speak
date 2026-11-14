---
story_id: 'US-009'
story_type: 'user_story'
title: 'Verbosity levels and skipping trivial replies'
epic: '4 Smarter speech'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 9
---

# US-009: Verbosity levels and skipping trivial replies

> GitHub issue [#9](https://github.com/lucaschallamel/claude-speak/issues/9) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- A `verbosity` setting:
  - `chime`: a short sound only.
  - `brief`: today's behaviour.
  - `detailed`: up to about 60 words.
- Skip replies like "Done." or "OK." when no tool ran.

Hearing "Done." after a quick question is noise. Sometimes you want more detail.

## Acceptance Criteria

- [ ] **AC1**: Each level works. Trivial replies are silent at `brief`.

Depends on the unit test suite story, so the change lands with tests.

Effort: S. Could go upstream: yes.

## Technical Requirements

- Add to `DEFAULTS`, `OVERRIDABLE`, the `plugin.json` `userConfig` and the `/speak-settings` menu.
- `detailed` uses its own prompt. `chime` plays a bundled short WAV through the server.
- The skip gate goes in the `cmd_hook` Stop path. Never skip AskUserQuestion or permission prompts.
