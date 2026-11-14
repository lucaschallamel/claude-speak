---
story_id: 'US-010'
story_type: 'user_story'
title: 'French and multilingual replies with a matching voice'
epic: '4 Smarter speech'
priority: 'Medium'
story_points: 3
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 10
---

# US-010: French and multilingual replies with a matching voice

> GitHub issue [#10](https://github.com/lucaschallamel/claude-speak/issues/10) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

When the reply is in French or another language Kokoro supports, summarize in that language and speak it with a matching voice.

Today French text is read by an English voice, which mangles it.

## Acceptance Criteria

- [ ] **AC1**: A French reply is summarized and spoken in French.
- [ ] **AC2**: A reply with English code inside French prose still counts as French.

## Technical Requirements

- Guess the language in the client, e.g. stopword counts for fr/es/it/pt, Unicode ranges for CJK.
- A `voice_by_lang` setting, e.g. `{"fr": "ff_siwis"}`.
- Add "Answer in {language}" to the summary prompt.
- `server.py` needs no change, because `LANGS` already maps a voice's first letter to its language.

## Risk

`ff_siwis` is Kokoro's only French voice, and its quality is lower than the English voices.

Effort: M. Could go upstream: yes.
