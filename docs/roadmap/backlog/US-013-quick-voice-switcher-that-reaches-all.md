---
story_id: 'US-013'
story_type: 'user_story'
title: 'Quick voice switcher that reaches all 54 Kokoro voices'
epic: '3 Characters'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 13
---

> [!note]- Progress updates
>
> - **2026-11-14**: Story file created from GitHub issue #13 (filed 2026-11-07); status Draft.

# US-013: Quick voice switcher that reaches all 54 Kokoro voices

> GitHub issue [#13](https://github.com/lucaschallamel/claude-speak/issues/13) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

A fast way to change voice without the 4-question `/speak-settings` menu, which offers only 4 of the 28 English voices.
- `/speak-voice male`, `/speak-voice female`: flip gender, keep the accent.
- `/speak-voice us`, `/speak-voice uk`, `/speak-voice fr`: switch language or accent, keep the gender when that language has one. French has only `ff_siwis`.
- `/speak-voice next` and `/speak-voice random`: browse voices.
- `/speak-voice <name>`: set an exact voice.
- With no argument: a menu grouped by language and gender, with short descriptions.
- Every change plays a short sample, as `config --preview` does today.

Kokoro names say what each voice is (first letter = language, second = gender, e.g. `bm_george`), but users can't browse them. Finding the right character's voice should take seconds.

## Acceptance Criteria

- [ ] **AC1**: Each argument picks a valid voice and plays a sample.
- [ ] **AC2**: An argument with no match (e.g. `male` while on `ff_siwis`) says why and changes nothing.

## Technical Requirements

- Add `skills/speak-voice/SKILL.md`, as thin as the other skills: one `claude-speak voice <arg>` call.
- Add a `voice` subcommand in `claude_speak.py` that works out the target from the `VOICES` list and the naming rule, then reuses the existing `config --voice ... --preview` path.
- Store a one-line description per voice for the menu, e.g. from Kokoro's VOICES.md grades.
