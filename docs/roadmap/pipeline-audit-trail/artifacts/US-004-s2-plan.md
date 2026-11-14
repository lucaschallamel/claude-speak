# US-004 S2 Plan: Instant replay and global stop/replay hotkeys

**Date**: 2026-11-14 | **Profile**: standard | **Story**:
[US-004](../../backlog/US-004-instant-replay-and-global-stop-replay.md) | **Input**:
[S1 kickoff](US-004-s1-kickoff.md)

**Purpose**: how US-004 will be built, the alternatives weighed, and what could go wrong.
**Audience**: Lucas and the agent running S3.

## Design

### Server (`scripts/server.py`)

- `Job` gains an optional `clip` (stored chunk samples plus their sample rate). A job with a clip is
  a replay.
- New `Speaker._audio(job)` generator yields `(samples, rate)` per chunk: from `job.clip` for a
  replay, otherwise from `split_chunks(job.text)` through `synth`, stopping when the job is
  cancelled. `_run`'s producer loops over it and keeps the lead-in and temp-WAV code as it is.
  This separation keeps the new logic testable without numpy (CI runs with numpy stubbed).
- New `Speaker._remember(job, chunks, rate)`, called once the producer has every chunk: stores the
  clip per session with a timestamp and records that session as the most recent. It ignores
  replays, cancelled jobs and empty results, and drops sessions not stored to for an hour.
- New `Speaker.replay(session="") -> bool`: under `state_lock`, picks the session's clip (or the
  most recent one), returns `False` when there is none; otherwise cancels the playing clip
  (`_cancel_current`), inserts the replay job at the front of the queue, sets `busy_until` and
  wakes the loop.
- `POST /replay {"session"?}`: `200 {"ok": true}` or `404 {"error": "nothing to replay"}`.
  Listed in the module docstring and in CLAUDE.md.

### Client (`scripts/claude_speak.py`)

- `claude-speak again [--session ID]`: if `server_health()` is false, prints
  `claude-speak: nothing to replay.` and returns; otherwise POSTs `/replay` and prints
  `claude-speak: replaying.` on 200, or the "nothing to replay" line on 404. It never calls
  `ensure_server`. It is wired like `stop` (own `--data-dir`).

### Docs

- README "Hotkeys" section in the fork additions: the wrapper script, binds for stop and replay
  in Hyprland's classic syntax and Omarchy's Lua syntax (`o.bind(...)`), and the
  `claude-speak stop; voxtype record start` barge-in for setups with no state file.

Wrapper (to be checked on omarchy at S6):

```sh
#!/bin/sh
# claude-speak for hotkeys: the newest installed plugin, talking to its server.
root=$(ls -d "$HOME"/.claude/plugins/cache/claude-speak/claude-speak/*/ | sort -V | tail -n 1)
export CLAUDE_SPEAK_DATA="${CLAUDE_SPEAK_DATA:-$HOME/.claude/plugins/data/claude-speak-claude-speak}"
exec "${root}bin/claude-speak" "$@"
```

### Tests (stdlib `unittest`, no numpy needed)

| Test                                                            | AC  |
| --------------------------------------------------------------- | --- |
| `_audio` on a replay job yields the stored chunks; `synth` never called | AC1 |
| `replay()` puts the job first in the queue and cancels the current job | AC3 |
| `replay()` returns `False` with nothing stored; with a session, picks that session | AC2, AC4 |
| `_remember` ignores replays and cancelled jobs; drops stale sessions | AC4 |
| client `again`: server down prints "nothing to replay", no `ensure_server`; 404 likewise; 200 prints "replaying" | AC2 |

## Alternatives considered

| #   | Alternative                                              | Verdict  | Why                                                                                                           |
| --- | -------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------- |
| A1  | Re-synthesise from stored text (client or server)        | Rejected | Simplest, but a summary takes about a second to synthesise; misses AC1 (under 300 ms).                         |
| A2  | Keep the temp WAV files on disk instead of samples        | Rejected | Needs cleanup and outlives the server; the issue asks for memory only. Samples are already in memory.           |
| A3  | Store one global clip instead of one per session          | Rejected | Saves a dict, but the issue's API takes a session, and per session costs about 2 MB each with the hour cutoff.  |
| A4  | Change `data_dir()` to find the plugin's data dir        | Rejected | Lucas chose the README wrapper (S1 decision 2).                                                                 |
| A5  | Replay waits behind the current clip                     | Rejected | Lucas chose interrupt, queue kept (S1 decision 1).                                                              |

## What could go wrong

| #   | Risk                                                                                      | Mitigation                                                                                                     |
| --- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| W1  | A half-made clip is stored when synthesis is cancelled mid-way                           | `_audio` stops on cancel; `_remember` also refuses cancelled jobs. Test covers it.                              |
| W2  | Replay inserted between `_loop` popping a job and `_run` starting it                     | `_cancel_current` acts on `self.current`, set under the same lock as the pop, so the popped job is cancelled.   |
| W3  | A newer reply for the same session arrives while its replay is queued                    | `speak()` cancels the session's queued jobs, the replay included: the new reply wins, as it should.             |
| W4  | Tests need numpy, which CI does not install                                              | All new logic is in `_audio`, `_remember` and `replay`, which handle samples as opaque objects; tests pass lists. |
| W5  | `sort -V` behaves differently on macOS                                                    | macOS `sort` supports `-V`; the README notes the path assumption. Checked on omarchy at S6.                     |
| W6  | A hotkey still reaches the wrong server                                                   | The wrapper sets `CLAUDE_SPEAK_DATA`; `claude-speak status` through the wrapper shows the data dir. Checked at S6. |
| W7  | Barge-in or hush stops the replay                                                         | Intended: replay is ordinary speech once queued.                                                                |

## Sequence

1. Server: `Job.clip`, `_audio`, `_remember`, `replay`, `/replay`, docstring. Tests.
2. Client: `again`. Tests.
3. README hotkeys and CLAUDE.md endpoint. Run the full suite.
4. S3 commit; S4 review follows.
