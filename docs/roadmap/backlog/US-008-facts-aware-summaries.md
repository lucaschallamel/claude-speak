---
story_id: 'US-008'
story_type: 'user_story'
title: 'Facts-aware summaries: tests, files changed, commits'
epic: '4 Smarter speech'
priority: 'Medium'
story_points: 3
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 8
---

# US-008: Facts-aware summaries: tests, files changed, commits

> GitHub issue [#8](https://github.com/lucaschallamel/claude-speak/issues/8) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

Give the summarizer what actually happened this turn, so it can say "Tests pass, 3 files changed" rather than restate the prose.

The reply often hides the outcome. Tool results are the ground truth.

## Acceptance Criteria

- [ ] **AC1**: The summary of a turn that ran tests states the result.
- [ ] **AC2**: Turns with no tool use behave as before.

## Technical Requirements

- While reading the transcript tail, collect this turn's `tool_use` and `tool_result` entries.
  - Bash: regex the output for test results (pytest, jest, cargo, go test, unittest) and for `git commit`.
  - Edit and Write: count the files changed.
- Pass these to the summarizer in a short `<facts>` block, and add one line to `SUMMARY_PROMPT` telling it to prefer facts.
