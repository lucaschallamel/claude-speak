# US-005 S1 Kickoff: Priority lanes

**Date**: 2026-11-14 | **Profile**: standard | **Story**:
[US-005](../../backlog/US-005-priority-lanes.md) (issue #5)

**Purpose**: S1 review of US-005 (scope, ACs, feasibility, risks) and the input to the S2 plan.
**Audience**: Lucas and the agent running the pipeline.

Issue #5 was re-read on 2026-11-14 and has no comments, so the story file held everything known.

## Findings from the code

- **Within one session, lanes already exist.** `Speaker.speak` (`scripts/server.py`) calls
  `_cancel_session` first, so a newer `/speak` from the same session stops that session's speech at
  once, mid-chunk, even if it is playing. A question during the same session's status line is already
  heard at once. The story matters **across sessions**. Today the queue is FIFO across sessions, so
  session B's question waits for session A's speech to finish.
- **"Next chunk boundary" usually means "the end".** `split_chunks` packs sentences into chunks of
  up to `CHUNK_CHARS = 250` characters, about 15 s of speech. A 20-word summary is one chunk. Status
  lines over `SUMMARY_THRESHOLD = 280` characters are summarised to one sentence. Waiting for a chunk
  boundary therefore usually means waiting for the whole utterance.
- **Status lines rarely queue, but can arrive late.** `maybe_interject` only spawns a worker when the
  server reports `busy: false`. The worker may then spend seconds on a `claude -p` summary, and
  another session's speech may start in the meantime. That is how a stale status line reaches the
  queue.
- **Replay already outranks everything.** `Speaker.replay` cancels the current job and inserts at
  the front of the queue.
- **The client knows the event.** `cmd_hook` routes `PreToolUse` (`AskUserQuestion`), `Stop` and
  `PostToolUse` (`maybe_interject`) through `spawn_worker`. The worker job already carries the hook
  time `t`, which the hush check uses.
- **Mechanism to reuse.** US-004's cancel path (`_cancel_current` plus the 50 ms consumer poll) cuts
  at once. Its `Job.made` and `Clip` reuse the chunks already made, which resuming a preempted summary
  needs.

## Decisions (Lucas, 2026-11-14)

1. **Status lines are cut at once.** A higher-priority job cuts a playing status line immediately,
   as replay and same-session replacement already do. A playing Stop summary is cut only at its next
   chunk boundary, so a question waits at most one chunk of a summary and never waits for a status
   line.
2. **A preempted summary resumes.** A Stop summary interrupted by a higher-priority job goes back to
   the front of its lane. It continues from its first unplayed chunk, reusing the chunks already
   made. A preempted status line is dropped.
3. **Staleness is measured from the hook, at both ends.** The client sends the hook time. The worker
   drops a status line whose summary took over 5 s, and the server drops a status line that waited
   over 5 s before it started. A status line that has started is not dropped for age, only preempted.
4. **Replay stays above everything.** `again` keeps its US-004 behaviour: it interrupts at once and
   goes to the front, ahead of questions too.

## Challenge Log

**Story**: US-005 | **Profile**: standard | **Entries**: 7

| #   | Aspect               | Challenge                                                                                                                       | Disposition                                                                                                                        | Status   |
| --- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 1   | Scope stress-test    | Same-session replacement already preempts. Is the story needed at all?                                                          | Yes, across sessions: the queue is FIFO across sessions. Story and ACs now say "another session".                                 | resolved |
| 2   | AC testability       | AC1 "within one chunk" is vague when a chunk can be 15 s.                                                                       | Split by what is playing: a status line is cut at once; a summary at its next chunk boundary (decision 1). Both are unit-testable. | resolved |
| 3   | AC testability       | AC2 "never spoken": against which clock?                                                                                        | The hook time, checked in the worker and in the server queue (decision 3). Tested with an injected clock and a backdated job.      | resolved |
| 4   | Risk surfacing       | The story does not say what happens to the interrupted speech. Dropping a summary loses the reply the user waited for.           | Resume from the first unplayed chunk, reusing made chunks; status lines are dropped (decision 2). New AC3.                         | resolved |
| 5   | Risk surfacing       | `priority` comes over the socket (a trust boundary since US-004). An unknown value must not crash or jump the queue.            | Allow-list of three values; missing or unknown means `normal`. Older clients keep today's behaviour. New AC5.                     | resolved |
| 6   | Dependency freshness | Builds on US-004's reworked `_run` loop and replay. Is it merged and current?                                                   | Yes: main `be27e10` contains US-004 (`ea64f0a`) and its close (`d8767f9`). US-006 (permission prompts) will reuse the urgent lane. | resolved |
| 7   | Risk surfacing       | Chunk-boundary preemption needs the consumer to check the queue between chunks while the producer may hold `synth_lock`.        | S2 plans the check point and measures question latency on real hardware (story rule: measure before done).                       | open     |

Entry 7 stays open until it is measured in S3/S6. It does not block S2.

## Implementation outline (for S2)

1. Client: `priority` on the worker job and in `send_to_server`. `PreToolUse` `AskUserQuestion` is
   `urgent`, `Stop` and `/speak` are `normal`, and interjections are `low`. The worker drops a `low`
   job older than 5 s and sends the hook time with the request.
2. Server: validate `priority`. Insert by lane, FIFO within a lane, with replay always at the front.
   On arrival, cut a playing lower-priority status line at once, or mark a playing summary for
   preemption at its next chunk boundary. Re-queue a preempted summary from its first unplayed chunk.
   Drop a `low` job older than 5 s when it is picked up.
3. Tests for each AC. Real-hardware run: two sessions, a status line or summary playing, then a
   question.
4. Docs: README (fork additions), CLAUDE.md (`/speak` body), docstring at the top of `server.py`.

## Risks

| ID  | Risk                                                                          | P   | I   | Mitigation                                                                        |
| --- | ----------------------------------------------------------------------------- | --- | --- | --------------------------------------------------------------------------------- |
| R1  | Resume replays or skips a chunk at the boundary (off by one).                  | M   | M   | Track the played count explicitly; test a 3-chunk summary preempted after chunk 1. |
| R2  | Question latency is dominated by synthesis held behind the current job's lock. | M   | M   | Measure; the producer stops synthesising once its job is marked preempted.         |
| R3  | More divergence from upstream in `Speaker`.                                    | H   | L   | Record in `memory-bank/systemPatterns.md` "Fork divergences".                      |
