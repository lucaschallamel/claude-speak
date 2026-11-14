---
story_id: 'US-005'
story_type: 'user_story'
title: 'Priority lanes: urgent speech preempts chatty speech'
epic: '2 Quiet'
priority: 'Medium'
story_points: 3
status: 'In Progress'
assignee: ''
author: 'Claude Code'
created: '2026-11-07'
last_modified: '2026-11-14'
github_issue: 5
---

> [!note]- Progress updates
>
> - **2026-11-14**: [S1_KICKOFF] Issue #5 re-read (no comments). Scope narrowed to cross-session preemption (same-session replacement already cuts at once); 4 decisions from Lucas; ACs 2 -> 5; challenge log 7 entries; standard profile kept.
> - **2026-11-14**: [S0_SELECT] Story selected; Orca worktree us-005-priority-lanes and branch feature/US-005-priority-lanes created from main be27e10; pipeline initiated, standard profile.
> - **2026-11-14**: Story file created from GitHub issue #5 (filed 2026-11-07); status Draft.

# US-005: Priority lanes: urgent speech preempts chatty speech

> GitHub issue [#5](https://github.com/lucaschallamel/claude-speak/issues/5) is the tracker and discussion; this file is the spec. Keep both in step: status changes here, decisions also as issue comments.

## Story Overview

Rank speech by priority: permission prompt or question, then the Stop summary, then mid-turn status lines.

A question or a permission request must not wait behind a status line. A status line that is no longer current is not worth hearing.

Within one session this already holds: a newer `/speak` from the same session stops that session's speech at once. This story is about speech from **other sessions**, which today plays first come, first served.

## Acceptance Criteria

- [ ] **AC1**: With another session's status line playing, an AskUserQuestion prompt cuts it at once. With another session's Stop summary playing, the prompt starts at that summary's next chunk boundary, never mid-chunk.
- [ ] **AC2**: A status line is never spoken once 5 s have passed since its hook fired before it started: the worker drops it after a slow summary, and the server drops it after waiting in the queue. A status line that has started is not dropped for age.
- [ ] **AC3**: A Stop summary interrupted by higher-priority speech resumes after it from its first unplayed chunk, reusing the chunks already made, with no chunk repeated or skipped. An interrupted status line is dropped.
- [ ] **AC4**: Order is replay, then `urgent` (questions), then `normal` (Stop summaries, `/speak`), then `low` (status lines), first come first served within a lane. A replay still interrupts at once and goes first. Same-session replacement is unchanged.
- [ ] **AC5**: `/speak` accepts `priority` (`urgent`, `normal`, `low`). A missing or unknown value means `normal`, so older clients behave as before. README, CLAUDE.md and the `server.py` docstring describe the field and the lanes.

## Technical Requirements

- Add a `priority` field to `/speak`. The client sets it per hook event: `PreToolUse` `AskUserQuestion` is `urgent`, `Stop` and `/speak` are `normal`, interjections are `low`.
- `server.py` orders the queue by lane. A higher-priority arrival cuts a playing `low` job at once. It marks a playing `normal` job to stop at its next chunk boundary from `split_chunks`, then re-queues the rest at the front of the `normal` lane.
- Drop `low` jobs older than 5 s, measured from the hook time the client sends, in the worker and when the server picks up the job.
- Measure the question's latency on real hardware with two sessions before calling the story done.

## Decisions (2026-11-14)

Lucas chose these at S1. The full reasoning is in `docs/roadmap/pipeline-audit-trail/artifacts/US-005-s1-kickoff.md`.

1. Status lines are cut at once. Summaries are cut at a chunk boundary.
2. A preempted summary resumes from its first unplayed chunk. A preempted status line is dropped.
3. Staleness is measured from the hook time, both in the worker and in the server queue.
4. Replay (`again`) stays above every lane.
