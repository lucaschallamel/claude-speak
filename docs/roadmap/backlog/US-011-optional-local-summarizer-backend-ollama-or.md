---
story_id: 'US-011'
story_type: 'user_story'
title: 'Optional local summarizer backend (Ollama or heuristic)'
epic: '4 Smarter speech'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 11
---

# US-011: Optional local summarizer backend (Ollama or heuristic)

> GitHub issue [#11](https://github.com/lucaschallamel/claude-speak/issues/11) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

A `summary_backend` setting with values `claude` (default), `ollama` or `none`.
- `ollama`: summarize with a local model through `localhost:11434/api/generate`, using stdlib `urllib`.
- `none`: a heuristic, the first sentence plus facts from the facts-aware story.

`claude -p` takes about 3 s, needs the network and uses quota. A local 1-3B model can write 20 words in under 1 s. The heuristic also covers a missing `claude` binary.

## Acceptance Criteria

- [ ] **AC1**: Each backend produces a spoken line.
- [ ] **AC2**: When Ollama is down, it falls back to the heuristic and logs it.

## Technical Requirements

- Branch in `_ask_claude`.
- Small models ignore the `[mood gesture]` format, so when `CUE` doesn't match, fall back to `[neutral none]`.
