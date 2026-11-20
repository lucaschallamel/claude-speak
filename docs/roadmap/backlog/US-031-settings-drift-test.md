---
story_id: 'US-031'
story_type: 'user_story'
title: 'Settings drift test'
epic: '3 Smarter speech'
priority: 'High'
story_points: 1
status: 'Done'
assignee: ''
author: 'Claude Code'
created: '2026-11-16'
last_modified: '2026-11-20'
github_issue: 31
---

> [!note]- Progress updates
>
> - **2026-11-16**: Story file created from GitHub issue #31, filed by the backlog review of 2026-11-16; status Draft.
> - **2026-11-20**: [S0_SELECT] Story selected, pipeline initiated on branch `lucaschallamel/US-031-settings-drift-test` (Orca worktree); status In Progress, card DOING, lightweight profile.
> - **2026-11-20**: [S1_KICKOFF] Scope refined: the skill check maps keys to `config` flags, default values compared too (Lucas); AC1 widened; points stay 1.
> - **2026-11-20**: [S3_EXECUTE] `SettingsDriftTest` added (4 tests, 146 in all, OK); six mutations each fail the expected test; CLAUDE.md names the test.
> - **2026-11-20**: [S4-S6] Fresh reviews S4 and S5 PASS, every finding mitigated (skill check limited to `config` lines, real `config` parser checked through `--help`); quality gates all pass (146 tests, Python 3.10, ruff, validators).
> - **2026-11-20**: [S7_CRITICAL_REVIEW] Fresh DoD review PASS; the AC1 WARN (a flag only in the skill passed) fixed with a skill-to-parser check; 147 tests.
> - **2026-11-20**: [S8_CAPTURE] Dev journal, memory bank and README review captured.
> - **2026-11-20**: [S9_CLOSE] Close documentation committed; status stays In Progress until the merge (Done and card DONE in the close PR).
> - **2026-11-20**: [S10_MERGE] PR #43 squash-merged as de4a0ee on Lucas's approval (CI 4/4 green on 9aa9021); issue #31 closed; story Done, card DONE, pipeline completed.

# US-031: Settings drift test

> GitHub issue [#31](https://github.com/lucaschallamel/claude-speak/issues/31) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

- A unit test that fails when a setting is added in one place but not the others.

CLAUDE.md requires every new setting in `DEFAULTS`, `plugin.json` `userConfig`, `OVERRIDABLE` (if user-toggleable) and the `speak-settings` skill. Nothing enforces it, and the next stories add settings.

## Acceptance Criteria

- [x] **AC1**: The test passes on main and fails when a setting is added to only one of those places,
  or when a default value differs between `DEFAULTS` and `userConfig`.

Effort: XS. Could go upstream: yes.

## Technical Requirements

- `set(DEFAULTS) == set(userConfig)` (both hold `auto_speak`, `speed`, `summarize`, `summary_model`, `voice` today).
- Each `DEFAULTS` value equals the `default` of the same key in `userConfig`.
- `OVERRIDABLE` is a subset of `DEFAULTS`.
- Every `OVERRIDABLE` key's `config` flag appears in `skills/speak-settings/SKILL.md`. The flag is `--` plus the key with dashes, except `auto_speak`, whose flag is `--auto`; the test holds that one exception.
- Every `OVERRIDABLE` key's flag is accepted by the real `config` parser, read through `config --help` (S5: `main()` uses `parse_known_args`, so a flag the parser lacks would be dropped without an error).
- Every flag on a `claude-speak config` line of the skill is accepted by the `config` parser (S7: a flag only in the skill would be dropped silently).
- One test class in `tests/test_client.py`, stdlib only. No runtime or skill change.

## Decisions (S1, 2026-11-20)

- The skill names `config` flags, not keys, so the test maps key to flag (`auto_speak` -> `--auto`) instead of editing the skill (Lucas).
- Default values are compared too, not only keys (Lucas).
- Not covered: how `cmd_config` handles each flag (its hand-written key lists) and the per-call flags in `with_voice()`. Since S5 the test does check that `config` accepts each flag. A key that is deliberately absent from `userConfig` would need an explicit exception, decided in the story that adds it.
- Points stay at 1.

## Decisions (after S3, 2026-11-20, Lucas)

- Branch pushed after the S3 checkpoint; no PR until S10.
- Three fresh-context reviews (S4, S5, S7), as the pipeline requires.
- S5 records the trust-boundary line: no trust-boundary path is touched (test-only change).
- The `cmd_config` and `with_voice()` gap stays a note here; no issue filed. US-009 and US-032 touch `cmd_config` anyway.
- Upstream: in the later batch with US-030 and the Quiet features. No version bump: no release.
