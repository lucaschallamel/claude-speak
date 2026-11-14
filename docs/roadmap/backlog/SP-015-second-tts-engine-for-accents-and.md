---
story_id: 'SP-015'
story_type: 'spike'
title: 'Spike: second TTS engine for accents and languages Kokoro lacks (Australian, richer French)'
epic: '4 Smarter speech'
priority: 'Medium'
story_points: 3
status: 'Draft'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 15
research_question: 'Which local, offline TTS engine fills Kokoro''s gaps (Australian English, richer French) well enough to be worth a second model?'
time_box: '2 days'
expected_outcome: 'Recommendation (or not worth it) on issue #15 with samples; if yes, a follow-up story for engine-prefixed voices'
decision_deadline: 2027-01-31  # placeholder for: before milestone 4 Smarter speech starts
---

> [!note]- Progress updates
>
> - **2026-11-14**: Story file created from GitHub issue #15 (filed 2026-11-07); status Draft. Time box 2 days and decision deadline before milestone 4 set by Lucas (2027-01-31 is a placeholder date).

# SP-015: Spike: second TTS engine for accents and languages Kokoro lacks (Australian, richer French)

> GitHub issue [#15](https://github.com/lucaschallamel/claude-speak/issues/15) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Question

Kokoro has no Australian English and only one French voice (`ff_siwis`, rated lower than the English voices). Which local, offline engine fills those gaps well enough to be worth a second model?

## Scope (research only, no code merged)

- Candidates: Piper first (local, ONNX, light). Others if Piper falls short.
- For each, check:
  - Is there an Australian English voice? Male and female?
  - How many French voices, male and female, and how good are they?
  - Licence (it must allow redistribution through the plugin's download step).
  - Model size, RAM, latency on a laptop CPU, macOS and Linux support.
  - Can it run in `server.py`'s uv environment next to Kokoro, and does it fit `split_chunks` streaming?
- Listen to samples of the same 2-3 summary lines in each candidate voice.

## Output

- A short write-up in this issue: a recommendation, or "not worth it", with sample links or files.
- If yes, a follow-up story: an engine prefix in voice names (e.g. `piper:fr_FR-...`), download on first use, and the server routing each request to the right engine.

## Acceptance Criteria

- [ ] **AC1**: The Australian and French questions each have an answer backed by samples.

Effort: M (time-boxed spike).
