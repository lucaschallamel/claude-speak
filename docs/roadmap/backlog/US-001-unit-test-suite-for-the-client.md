---
story_id: 'US-001'
story_type: 'user_story'
title: 'Unit test suite for the client and server pure functions'
epic: '1 Foundation'
priority: 'Medium'
story_points: 2
status: 'Done'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 1
---

# US-001: Unit test suite for the client and server pure functions

> GitHub issue [#1](https://github.com/lucaschallamel/claude-speak/issues/1) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

Add a stdlib `unittest` suite. Run it with `python3 -m unittest discover tests`.

There are no tests. Most content stories change the same functions, and a change in Claude Code's transcript format would break speech without any error.

## Acceptance Criteria

- [x] **AC1**: The suite passes on Linux and macOS with no network, model or audio player.
- [x] **AC2**: CLAUDE.md lists the command, including how to run one test.

## Technical Requirements

- `tests/test_client.py`: `speakable`, the `CUE` regex, `last_response` and `current_status` on trimmed JSONL fixtures, `load_settings` precedence (defaults < options.json < `CLAUDE_PLUGIN_OPTION_*` < overrides.json < flags), the summary cache key, `is_own_reply`.
- `tests/test_server.py`: `split_chunks`, plus queue and replace behaviour with Kokoro stubbed out.
- `tests/fixtures/`: small transcripts with text, tool use, AskUserQuestion and the speak skills.
