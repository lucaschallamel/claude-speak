---
story_id: 'US-014'
story_type: 'user_story'
title: 'Voice blends: custom voices mixed from Kokoro style vectors'
epic: '3 Characters'
priority: 'Medium'
story_points: 2
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 14
---

> [!note]- Progress updates
>
> - **2026-11-14**: Story file created from GitHub issue #14 (filed 2026-11-07); status Draft.

# US-014: Voice blends: custom voices mixed from Kokoro style vectors

> GitHub issue [#14](https://github.com/lucaschallamel/claude-speak/issues/14) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

Let users define named blends of existing voices, e.g. `narrator = 0.6 bf_emma + 0.4 af_heart`. Use a blend anywhere a voice name works: settings, `/speak-voice`, `say --voice`.

54 base voices is not much range for characters. Blending gives an unlimited set of new, stable voices at no cost, with no new model and no download.

## Acceptance Criteria

- [ ] **AC1**: A named blend and an inline blend both speak.
- [ ] **AC2**: Weights are normalised.
- [ ] **AC3**: An unknown member voice gives a clear error rather than a silent fallback.

## Technical Requirements

- The installed kokoro-onnx supports this: `Kokoro.create()` accepts `voice: str | NDArray[np.float32]`, and `get_voice_style(name)` returns a voice's style vector. A blend is the weighted sum of those vectors.
- Blends live in `<data>/voices.json`, e.g. `{"narrator": {"bf_emma": 0.6, "af_heart": 0.4}}`. Also accept inline syntax such as `bf_emma:60,af_heart:40`.
- `server.py`: `resolve_voice()` today accepts only exact names and falls back to `af_heart`. Extend it to build and cache the blended vector.
- Language comes from the first voice in the blend, using the existing `LANGS` rule.
- `/speak-voice` gets `save <name>` to keep the current blend.

## Risk

Mixing voices from different languages gives odd results. Warn when a blend mixes languages.

Effort: S-M. Could go upstream: yes.
