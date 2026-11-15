---
entry_date: 2026-11-15
author: 'Lucas Challamel'
focus_area: 'US-005 priority lanes: urgent speech preempts chatty speech'
status: completed
session_duration: 'two sessions, 2026-11-14 and 2026-11-15'
tags: [us-005, priority-lanes, preemption, chunking, prefetch, server, cu-pipe, measurement]
version: '1.0.0'
last_updated: '2026-11-15'
maintained_by: 'Lucas Challamel'
---

**Session summary**: US-005 added priority lanes to the speech server through the full COPPER
pipeline. Real-hardware measurement and two hands-on rounds reshaped the design three times, and
the final design brings a question over another session's reply in at the next phrase, about 2 s,
where the first build made it wait 15 s.

## Why (High-Level Context)

With several Claude Code sessions talking, a question or a permission request should never wait
behind a status line, and a status line that is no longer current isn't worth hearing. Issue #5
asked for lanes: question, then the Stop summary, then mid-turn status lines.

**Session objectives**:

- Deliver US-005, the last story of milestone 2 Quiet, which unlocks the 0.4.0 release.
- Keep the change generic (no avatar code) so it can be offered upstream later (decision 17).

**Related work**:

- User story: [US-005](../../../roadmap/backlog/US-005-priority-lanes.md) (issue #5), milestone
  2 Quiet; builds on US-004's reworked playback loop; US-006 (spoken permission prompts) will
  reuse the `urgent` lane.
- Pipeline record: `docs/roadmap/pipeline-audit-trail/US-005.yaml`; kickoff and plan in
  `artifacts/US-005-s1-kickoff.md` and `artifacts/US-005-s2-plan.md`.

## How (The Journey)

### The Initial Problem

The S1 reading of `Speaker.speak` showed the story was smaller than it looked. Within one session,
a newer `/speak` already cancels that session's speech at once, so lanes only matter across
sessions, which played first come, first served. Lucas settled four decisions at S1: status lines
are cut at once, replies at a chunk boundary and then resumed, staleness counts from the hook,
and replay stays above everything. Two grilling sessions added decisions 5 to 17.

### The First Build (S3 round 1)

`/speak` gained `priority` (`urgent`, `normal`, `low`) and `at`, the hook time. The server inserts
by lane (`_enqueue`), cuts or flags the current job (`_preempt_for`), drops stale status lines when
it picks a job (`_next`), and on a chunk boundary re-queues a flagged reply from its first unplayed
chunk (`_resumed`, `Job.played`). The client sets the lane per hook event, and its worker drops a
status line that took over 5 s to summarise. Measured with real Kokoro and a logging `pw-play`
wrapper: a question came in 0.72-1.02 s over a playing status line.

### Dead Ends and Corrections

- **The "device wake" theory was wrong.** A question arriving before a status line was audible
  took 3.2 s, and I first blamed the 2 s Bluetooth lead-in. Measuring showed `/warm` doesn't help:
  the cost is the status line's own synthesis (2.3-3.2 s), which Kokoro can't interrupt. Lucas
  chose to fix this cold case in the story (AC6).
- **One sentence per chunk missed the bar by 0.01 s** (median 3.01 s against 3.0 s), because long
  sentences still take 2-3 s. Splitting long sentences at commas got it to 1.38 s.
- **The hands-on found what the measurements didn't.** Through `avatar-play`, a question over a
  reply waited about 15 s: the reply's 250-character chunk had to finish. Lucas chose one rule for
  all speech, about 80 characters per chunk (decision 21).
- **Small chunks created a new wait.** With 80-character chunks the reply's producer is always
  synthesising ahead, so a question waited for the lock and then its own synthesis. The fix was
  stop-ahead plus a prefetch of the question's first chunk (decision 22), so it starts 0.00 s
  after the boundary.
- **Load made measurements meaningless.** At load 13-18 (other sessions, builds, 14 GiB of swap)
  the same code ranged from 0.69 to 9.64 s. Measuring stopped until Lucas paused the other work;
  on the quiet machine every bar passed. AC1 now says "on a quiet machine" (decision 23), and the
  loaded tail is recorded as a known limit.

### Review Findings That Mattered

Seven fresh-context reviews (S4 three rounds, S5 twice, S7) found no Critical or High issues, but
several real Low ones:

- A huge integer `at` raised `OverflowError` after the session's speech had already been
  cancelled.
- A drain-thread leak in my own resume fix: it consumed the producer's end marker, and my
  ponytail review had missed it.
- A prefetch thread that failed to start would have left its question waiting forever.
- A flood of urgent requests started a thread per request; it is now one prefetch worker.
- A first version of one test hung under an injected bug instead of failing.

Every fix was pinned by a mutation check: remove the fix, see the test fail, restore from a
backup.

### Validation and Documentation

- 112 unit tests; 9 skip without numpy. CI now installs numpy on the Python 3.13 jobs, so the
  playback tests run on GitHub too, and has `permissions: contents: read`.
- Quiet machine, final design: status line median 0.74 s, worst 0.80 s (10 runs); reply 0.00 s
  after the chunk; cold case median 1.16 s, worst 1.39 s; stale lines dropped.
- Hands-on (Lucas, `avatar-play`): the cut, a 2.0 s wait over a reply, a seamless resume and
  natural 80-character pieces were all confirmed by ear. A first silent run was the avatar page's
  audio, not the pipeline.
- Docs: README "Priority lanes", the CLAUDE.md server paragraph, the `server.py` docstring,
  `systemPatterns.md` fork divergences, and the `techContext.md` CI note.

## Final State & Next Steps

**Current state**: all of US-005's code is on `feature/US-005-priority-lanes`, reviewed and tested
at S7 (`e9410f8`). Close documentation and the PR are next (S9, S10).

**Next steps**:

- [ ] S9 close docs: fold in the story overview note (permission prompts are US-006's scope) and
      put AC5 before AC6.
- [ ] S10: re-run the battery, open the PR, check that the CI matrix with numpy on 3.13 goes green.
- [ ] Release 0.4.0 with the laptop update block, which ends the running `server.py` (`claude-speak stop` only stops playback) after
      updating.

**Knowledge to preserve**:

- Measure latency on a quiet machine and record the load with every set. Kokoro's timing under
  load is dominated by other processes.
- Kokoro synthesis can't be interrupted, so chunk size bounds how long preempting speech waits.
- When the producer stops early, the consumer must still resume, and any end marker it consumed
  must be put back for the drain thread.

## Reflection

**What went well**: measuring before believing. Every design change came from a number or from
Lucas listening, not from a guess. The hard gates and fresh reviewers caught real defects each
round.

**What could improve**: I claimed "Looks good. Ship." on round 3 before the fresh reviewer found a
leak in my own fix. I also measured under heavy load before checking the load. Both now have a
standing rule: check the load first, and don't call ship before the independent review.
