# US-005 S2 Plan: Priority lanes

**Date**: 2026-11-14 | **Profile**: standard | **Story**:
[US-005](../../backlog/US-005-priority-lanes.md) (issue #5) | **Input**:
[S1 kickoff](US-005-s1-kickoff.md)

**Purpose**: how US-005 will be built: the chosen design, the alternatives rejected, what could go
wrong, and how each acceptance criterion is checked. **Audience**: Lucas and the agent running the
pipeline.

## Design

### Server (`scripts/server.py`)

New constants, next to the replay ones:

- `PRIORITIES = {"urgent": 0, "normal": 1, "low": 2}`. A smaller number plays first. Replay jobs use
  `-1` (`REPLAY_PRIORITY`), so they rank above every lane without a special case in the sort.
- `STALE_LOW = 5.0`: a `low` job not started this long after its hook is dropped.

`Job` gains four fields:

- `priority: int = 1`
- `at: float = 0.0`: hook time; 0 means unknown, and the enqueue time is used.
- `played: int = 0`: chunks fully played. A resume starts after them.
- `preempt: bool = False`: stop at the next chunk boundary and resume later.

`Speaker` changes:

1. `speak(..., priority="normal", at=None)` maps the name through `PRIORITIES`. A missing or
   unknown name means `normal` (AC5). `at` must be a finite number not in the future, otherwise
   `now` is used. A `low` job from a session whose current or queued job (not cancelled) is in a
   higher lane is dropped, and nothing is cancelled (decision 5). Otherwise `_cancel_session` runs
   (same-session replacement), then `_enqueue(job)`, then `_preempt_for(job)`.
2. `_enqueue(job, front=False)` inserts at the end of the job's lane: before the first queued job
   with a larger priority number. With `front=True` it inserts at the start of the lane: before the
   first job with an equal or larger number. Replay keeps `queue.insert(0, ...)` and gets
   `priority=REPLAY_PRIORITY`.
3. `_preempt_for(job)`, with `state_lock` held, acts only if a current job is running, not
   cancelled, from another session and in a lower lane (a larger number):
   - a `low` current job is cancelled at once through `_cancel_current` and dropped (decision 1, AC1,
     AC3);
   - a `normal` current job gets `preempt = True` (decision 1).
   An `urgent` current job, or a replay, is never preempted, and a job in the same lane never
   preempts another (FIFO, AC4).
4. Consumer loop in `_run`:
   - the check before spawning the next chunk becomes `if job.cancelled or job.preempt: break`;
   - so does the check in the 50 ms empty-queue poll, so a job waiting for synthesis also stops at
     the boundary;
   - after `_reap(proc)` returns, `job.played += 1`.

   The check sits between two chunks' playback, so a `normal` job never stops mid-chunk.
5. On the break path (with `state_lock`): if `job.preempt` and not `job.cancelled`, queue a resumed
   job with `_enqueue(..., front=True)`. Then set `job.cancelled = True`, so the producer stops
   synthesising, and start `drain()` as today. The resumed job is
   `Job(session, text, voice, speed, clip=Clip(list(job.made), rate, now), priority, at, played=job.played)`.
6. `_audio(job)` starts at `job.played`. It yields `clip.chunks[played:]`, then synthesises
   `split_chunks(text)[max(len(clip.chunks), played):]`. The resumed job starts with
   `made = clip.chunks[:played]`, so `_remember` still sees the whole utterance and `/replay` of a
   resumed job restarts from the top. Chunks already made but not played are reused (AC3).
7. `_loop` drops a `low` job when it pops it, if `time.time() - job.at > STALE_LOW`, and logs one
   line (AC2, server side).
8. The `/speak` handler passes `body.get("priority")` and `body.get("at")` through to `speak()`. The
   module docstring documents both fields and the lanes.

### Client (`scripts/claude_speak.py`, stdlib only)

- `spawn_worker(..., priority="normal")` stores `priority` in the worker job, next to the hook time
  `t` it already records.
- `cmd_hook` sends `priority="urgent"` for `PreToolUse` `AskUserQuestion`. `maybe_interject` sends
  `"low"`. `Stop` and the skills keep the default.
- `cmd_worker`: after `prepare()` and the hush check, a `low` job is dropped if
  `time.time() - job["t"] > STALE_LOW` (AC2, worker side). `send_to_server(..., priority, at)` adds
  both fields to the `/speak` body. The client keeps its own `STALE_LOW` constant: it cannot import
  `server.py`, because numpy and Kokoro are not stdlib.

### Decisions settled after the plan (grilling, 2026-11-14)

Decisions 5 to 11 in the story file: same-session status lines are dropped instead of replacing a
question or summary; any higher lane cuts a status line; no project name on resume; `STALE_LOW` is a
fixed constant; `maybe_interject` keeps its idle gate; AC1 gets a 1.5 s bar; wire values are
`urgent`, `normal` and `low`. Only decision 5 changed the design (step 1 above).

## Alternatives considered

| Option                                                                         | Why not                                                                                                                                                    |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `heapq` or one queue per lane                                                  | The queue holds a handful of jobs. A list with insert-by-lane keeps the existing `self.queue` code (stop, cancel, replay, `warm`) unchanged.                 |
| Client-side lanes: the client calls `/stop` on other sessions before speaking   | The client cannot see what other sessions are playing. It would race with them and could not resume a summary.                                              |
| Resume by re-synthesising the remaining text                                   | It wastes the chunks already made (decision 2 asks to reuse them) and adds a synthesis delay to the resume.                                                |
| Cut every lower lane at once (no chunk boundary)                               | Lucas chose a chunk boundary for summaries (decision 1).                                                                                                    |
| Pre-synthesise the urgent job's first chunk while the summary's chunk finishes | It would cut the question's latency further, but it needs a second synthesis path that `synth_lock` serialises anyway. Revisit only if the measurement says so. |

## What could go wrong

| #   | Risk                                                                                                                  | Mitigation / check                                                                                                                                                           |
| --- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W1  | Off by one at the boundary: a chunk repeated or skipped on resume.                                                    | `played` is incremented only after `_reap` returns. A test preempts a 3-chunk summary after chunk 1 and asserts the exact play order and the synthesis count.                 |
| W2  | Preemption is set while the last chunk plays: the job finishes, and a resume would replay nothing or loop.            | When the last chunk ends, the consumer gets `None` and returns without the break path, so no resume is queued. Test: preempt during the last chunk; nothing is re-queued.     |
| W3  | Preempted, then the same session speaks again, stops or hushes before the boundary.                                   | `_cancel_session` sets `cancelled`, and the break path re-queues only if not cancelled. A resumed job already queued is dropped by `_cancel_session` like any queued job. Test. |
| W4  | A replay arrives while a job is marked for preemption.                                                                | Replay cancels the current job (US-004 behaviour), so no resume is queued. Replay restarts that speech from the top anyway.                                                   |
| W5  | A bad `priority` or `at` over the socket (trust boundary).                                                            | Allow-list for `priority`. `at` goes through `float()` inside a `try`; anything non-finite or in the future becomes `now`. Never an exception or a queue jump. Tests.          |
| W6  | Question latency is dominated by the summary producer holding `synth_lock` mid-chunk.                                 | The producer stops after its current synthesis (`cancelled` on the break path). Measure on real hardware (S1 open entry 7); record the numbers in S6.                          |
| W7  | Flaky timing tests, as in US-004.                                                                                     | Reuse the `wait_until()` and `private_tmp()` helpers. Test the queue logic on the `speaker()` fixture without threads where possible.                                        |
| W8  | A clock jump makes every `low` job look stale, or none.                                                               | Acceptable: status lines are best effort. Same-machine `time.time()` on both ends, as the hush check already uses.                                                           |

## Test plan (unittest, `tests/test_server.py` and `tests/test_client.py`)

| AC  | Test                                                                                                                                         |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| AC1 | `low` current from A, `urgent` from B: current cancelled at once, its player terminated, B at the front, nothing re-queued.                    |
| AC1 | `normal` current from A, `urgent` from B: current gets `preempt`, is not cancelled, and keeps playing until its chunk ends.                   |
| AC2 | Server: a `low` job whose `at` is 6 s old is dropped when popped, and one 1 s old plays. Client: a `low` worker job whose `t` is 6 s old is never sent. |
| AC3 | `_run` with a fake player: a 3-chunk summary, preempt during chunk 1, then play order A1, B, A2, A3 with no repeats; A's chunks synthesised once each. |
| AC3 | W2, W3 cases above.                                                                                                                          |
| AC4 | Queue order for mixed lanes and sessions; FIFO within a lane; a replay first; same-session replacement tests still pass unchanged.           |
| AC4 | Same session: a `low` job while that session's `urgent` plays, or its `normal` is queued, is dropped and cancels nothing (decision 5). B's `normal` cuts A's playing `low` at once (decision 6). |
| AC5 | `priority` missing, `"bogus"` or `7` means `normal`; `at` of `"x"`, `inf` or the future means now; the `/speak` endpoint passes both fields through. |
| AC5 | Client: `PreToolUse` `AskUserQuestion` spawns with `urgent`, interjection with `low`, `Stop` with `normal`; `send_to_server` body has both fields. |

Real hardware (S3, before S4):
- Two `CLAUDE_SPEAK_DATA=/tmp/...` sessions against the worktree's server, using the logging player
  and `avatar-play`.
- Measure the time from the question's `/speak` to its first chunk reaching the player, with a
  status line and then a summary playing. Pass bar (decision 10): 1.5 s over a status line, and
  the rest of the playing chunk plus 1.5 s over a summary.
- Hear that the summary resumes without a repeat.

## Files

- Code: `scripts/server.py`, `scripts/claude_speak.py`.
- Tests: `tests/test_server.py`, `tests/test_client.py`.
- Docs:
  - `README.md` (fork additions);
  - `CLAUDE.md` (`/speak` body and lanes);
  - `server.py` docstring;
  - `memory-bank/systemPatterns.md` ("Fork divergences": the `_run` consumer and the `Speaker.speak`
    enqueue).
- No change to `hooks/hooks.json`, `plugin.json` or the settings. Lanes are not user-configurable,
  which keeps the change small.

## Not in scope

- Spoken permission prompts (US-006). This story only adds the `urgent` lane they will use.
- A settings switch to turn lanes off.
- Resuming speech interrupted by a replay.

## Estimate

About half a day: server about 60 lines, client about 15, tests about 150, docs. It stays within the
3-point estimate.
