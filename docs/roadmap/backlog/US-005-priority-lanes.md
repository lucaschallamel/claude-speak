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
> - **2026-11-15**: [S6_TEST_QUALITY_VERIFY] Gates pass on 9620c66 (112 tests, ruff, validator 16/16); hands-on through avatar-play confirmed by Lucas: question over a reply 2.0 s (was 15 s), seamless resume, natural pieces.
> - **2026-11-15**: [S5_ARCH_SEC_COMP_REVIEW] Delta review PASS (3 low, 4 info); not security-sensitive; prefetch start failure handled, one prefetch worker at a time, chunk count split once.
> - **2026-11-15**: [S4_CODE_REVIEW] Round 3 PASS (4 low, 3 info): drain-thread leak and stale-prefetch synthesis fixed, AC6 reworded, tests tightened; the leftover pause after a cancelled question accepted with reason.
> - **2026-11-15**: [S3_EXECUTE] Round 3 (from the S6 hands-on): one ~80-char chunk rule for all speech, stop-ahead and prefetch; quiet-machine measurement: status line median 0.74 s / worst 0.80 s, reply 0.00 s after the chunk, cold median 1.16 s / worst 1.39 s, stale dropped; 108 tests.
> - **2026-11-14**: [S5_ARCH_SEC_COMP_REVIEW] Fresh arch/security review PASS (2 low, 4 info); trust boundary touched, not security-sensitive; huge `at` no longer cancels speech, docs and CI permissions tightened; release note for 0.4.0.
> - **2026-11-14**: [S4_CODE_REVIEW] Round 2 PASS (2 low, 3 info); semicolon split, replay-truncation test, "about 80" wording.
> - **2026-11-14**: [S3_EXECUTE] Round 2: status lines split into sentence and comma pieces; cold case median 3.2 -> 1.38 s, worst 5.59 -> 1.58 s; AC1 bar now a median (decision 19); 103 tests.
> - **2026-11-14**: [S4_CODE_REVIEW] Fresh review PASS (3 low, 3 info); 4 fixed (CI numpy on 3.13, two test gaps, README), 2 accepted. Second grilling: 6 decisions (12-17); cold case fixed in this story (AC6), so S3 reopens.
> - **2026-11-14**: [S3_EXECUTE] Lanes, preemption, resume and stale drop built in server and client; 21 new tests (99 total); real Kokoro run: question 0.72-1.02 s over a status line, 0.77 s after a reply's chunk, resume without repeats, stale line dropped.
> - **2026-11-14**: [S2_PLAN] Plan written; grilling settled 7 more decisions (5-11): same-session status lines dropped, AC1 latency bar 1.5 s.
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

- [ ] **AC1**: With another session's status line playing, an AskUserQuestion prompt cuts it at once. With another session's Stop summary playing, the prompt starts at that summary's next chunk boundary, never mid-chunk. Measured on real hardware from the question's `/speak` to its first audio at the player: over a status line, a median under 1.5 s over 5 runs with no run over 2.5 s (decision 19); over a summary, within the rest of the playing chunk plus 1.5 s.
- [ ] **AC2**: A status line is never spoken once 5 s have passed since its hook fired before it started: the worker drops it after a slow summary, and the server drops it after waiting in the queue. A status line that has started is not dropped for age.
- [ ] **AC3**: A Stop summary interrupted by higher-priority speech resumes after it from its first unplayed chunk, reusing the chunks already made, with no chunk repeated or skipped. An interrupted status line is dropped.
- [ ] **AC4**: Order is replay, then `urgent` (questions), then `normal` (Stop summaries, `/speak`), then `low` (status lines), first come first served within a lane. Any higher lane from another session cuts a playing status line at once. A replay still interrupts at once and goes first. Within a session, a newer question or Stop summary still replaces older speech, but a status line never replaces that session's question or summary (playing or queued): it is dropped.
- [ ] **AC6**: Cold case: when a question arrives before another session's status line is audible and the output has been quiet for over 3 s, its first audio comes within a median of 3.0 s over 5 runs of the real flow (`/warm`, then `/speak`), and no run is slower than 5.6 s (the worst before the fix). All speech is cut into chunks of about `CHUNK_CHARS` (80) characters: sentences, long ones split at commas and semicolons, short ones packed together (decision 21), so a question waits for at most one short chunk of a status line it cuts.
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

Lucas settled these in a grilling session after S2:

5. Within a session, a status line never replaces the session's question or summary: it is dropped. A question or Stop summary still replaces older speech.
6. Any higher lane from another session cuts a playing status line at once, a Stop summary included.
7. A resumed summary does not repeat the project name.
8. `STALE_LOW = 5.0` is a fixed constant, not a setting or env var.
9. `maybe_interject` keeps its idle gate: status lines still start only when nothing is speaking.
10. AC1 has a latency pass bar of 1.5 s (see AC1).
11. Wire values are `urgent`, `normal` and `low`.

Lucas settled these in a second grilling session after S4:

12. S5 records "trust boundary touched, not security-sensitive"; no full security audit.
13. Hands-on listening happens at S6: a short script through `avatar-play`, judged by Lucas.
14. The cold case is fixed in this story (AC6): low-lane jobs are split one sentence per chunk (superseded by decision 21: one rule for all speech). Measured before the fix: a status line's synthesis takes 2.3-3.2 s and cannot be interrupted, the question's 0.74-0.98 s; the question's first audio came 2.85-5.59 s after its `/speak` with `/warm` (2.44-4.02 s without), on omarchy at load average 12. `/warm` does not help, because synthesis, not the device wake, dominates.
15. The AC6 bar: a median of 5 runs under 3.0 s, no run slower than 5.6 s. The lead-in is not changed: it protects first words on Bluetooth.
16. The fix goes back through S3, then a fresh S4 review of the new code, before S5.
17. Upstream: offer the generic Quiet features (barge-in, hush, replay, lanes) to upstream together, after 0.4.0 has run for a while. No upstream action in this story.
18. One sentence per chunk missed AC6 by 0.01 s (median 3.01 s, worst 4.18 s at load average 13), because a long sentence still takes 2-3 s to synthesise. Long status-line sentences are also split at commas (and, after the S4 round-2 review, semicolons) into pieces of about 80 characters (at most 81: the packing ignores the joining space, as it always has for replies). Measured after: median 1.38 s, worst 1.58 s.
19. That makes the AC1 tail slower: while one piece plays, the next is being synthesised, and a question waits for it. Over 8 runs: median 1.08 s, two runs over 1.5 s (1.58, 1.93). The AC1 bar over a status line becomes a median of 5 under 1.5 s with no run over 2.5 s, the same form as AC6. Across both cases the worst wait fell from 5.59 s to 1.93 s.

Lucas settled these at the S6 hands-on (through `avatar-play`):

20. Status-line pauses sound natural. A status line cut by another session's question sounds right: a cut, a short pause, then the question.
21. A question over a reply waited about 15 s, for the reply's whole 250-character chunk. All speech now uses one chunking rule: sentences, long ones split at commas and semicolons, short ones packed to about 80 characters (`CHUNK_CHARS = 80`). The separate status-line mode is gone.
22. With small chunks the reply's producer is always synthesising ahead, so the question waited for its own synthesis after the boundary (about 2 s under load). Now the preempted reply stops synthesising, and the question's first chunk is synthesised while the reply's chunk finishes (`_prefetch`). Measured: the question starts 0.01 s after the reply's chunk ends.

## Release notes (for 0.4.0)

- After updating, run `claude-speak stop` (or wait up to `CLAUDE_SPEAK_IDLE_TIMEOUT`, 30 minutes): a server started by the old version keeps running without lanes until it exits (S5 finding 6). Put this in the laptop update block.
