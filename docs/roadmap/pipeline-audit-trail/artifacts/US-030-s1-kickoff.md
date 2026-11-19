# US-030 S1 Kickoff: Restart a stale server after a plugin update

**Date**: 2026-11-19 | **Profile**: standard | **Story**:
[US-030](../../backlog/US-030-restart-a-stale-server-after-a.md) (issue #30)

**Purpose**: S1 review of US-030 (scope, ACs, feasibility, risks) and the input to the S2 plan.
**Audience**: Lucas and the agent running the pipeline.

Issue #30 was re-read on 2026-11-19 and has no comments, so the story file held everything known.

## Findings from the code

- **One socket for every version.** `socket_path()` (`scripts/claude_speak.py`) hashes the data
  dir, and the data dir (`~/.claude/plugins/data/claude-speak-claude-speak/`) survives updates. A new
  client therefore finds the old server on the same socket and uses it: that is the bug.
- **`ensure_server()` returns at the first healthy answer.** It checks `/health` before and after
  taking `server.lock`. Both checks must also compare versions, and the lock already serialises
  concurrent starts, so several workers that see a stale server at once start one new server.
- **"Busy" already means queued or playing.** `Speaker.busy_until` is set an hour ahead on
  `/speak` and `/replay`, and set to now when the queue empties (`scripts/server.py`). `/health`
  reports it as `busy`. The idle watcher already refuses to exit while busy. `/quit` can reuse it.
- **The idle watcher ticks every 15 s.** A quitting server would wait up to 15 s after the queue
  empties. `/quit` needs a faster path (an event the watcher waits on).
- **The version is in `.claude-plugin/plugin.json`** (`"version": "0.4.0"`), next to `scripts/` in
  both the repository and the installed plugin cache. Both processes can read it from their own
  location. The client is stdlib only and the server is a separate script, so each reads it with a
  few lines of its own.
- **Callers of `ensure_server()`:** `send_to_server` (detached workers and `say`) and `cmd_setup`.
  `cmd_again`, `cmd_stop` and `cmd_status` never start a server and stay as they are, except that
  `status` will print the server's version, to check AC1 by hand.

## Review criteria

- Scope: bounded to the two scripts, their tests and docs. No new setting.
- Requirements: AC1 and AC2 are observable on real hardware; AC3 is unit-testable.
- Feasibility: stdlib only on the client; no new dependency on the server.
- DoD: unit tests, hands-on check with a worktree server and its own `CLAUDE_SPEAK_DATA`, docs.

## Challenge Log

**Story**: US-030 | **Profile**: standard | **Entries**: 7

| #   | Aspect               | Challenge | Disposition | Status |
| --- | -------------------- | --------- | ----------- | ------ |
| 1   | Scope stress-test    | Servers from before this story (0.4.0 here, 0.3.3 on the laptops) have no `/quit` and report no version. "No manual step" cannot hold for the first update to 0.5.0 without a kill path. | Lucas chose one last manual step: automatic restarts hold from 0.5.0 onwards; the 0.5.0 update block keeps the `pkill` line once. A server with no version is still treated as stale (the client sends `/quit`, gets an error, and uses it at once, with no wait). AC1 reworded. | resolved |
| 2   | Risk surfacing       | Two Claude Code sessions on different plugin versions (one restarted after an update, one not) would each restart the other's server in turn, forever. | Restart only when the server's version is **older** than the client's (numeric compare of the dotted version). An older client uses a newer server: the API only grows. New AC4. | resolved |
| 3   | Risk surfacing       | A chatty session could keep the old server busy forever, so it never drains. | A quitting server answers new `/speak` and `/replay` with 503. Speech from an old client during the drain is lost (logged); the new client's own speech waits for the new server. | resolved |
| 4   | AC testability       | How long does the client wait for the old server to exit? A long reply can play for 30 s or more. | Workers are detached, so waiting costs nothing visible. Wait up to 120 s for the socket to stop answering; past that, log and speak through the old server rather than lose the speech. | resolved |
| 5   | Risk surfacing       | The idle watcher ticks every 15 s, so the drain would add up to 15 s of silence after the old speech. | `/quit` sets an event the watcher waits on, and the speaker loop sets it when the queue empties; exit within about a second of the last chunk. Measured on real hardware at S6. | resolved |
| 6   | Dependency freshness | Does anything else start a server or rely on the socket staying up? | Only `ensure_server()` starts one. `again`, `stop`, `status` tolerate a missing server already. The worktree server uses its own data dir, so tests never touch the installed one. | resolved |
| 7   | Estimate             | Story points were 2, set before the code was read. | Re-estimated to 3: server endpoint and drain, client compare and wait, tests on both sides, a hands-on run. Actual effort goes in the dev journal. | resolved |

## Risk register

| ID | Risk | Probability | Impact | Mitigation |
| -- | ---- | ----------- | ------ | ---------- |
| R1 | Version ping-pong between sessions | Medium | High | Restart only for an older server (AC4), unit test |
| R2 | Speech lost during the drain | Low | Low | Only old clients' speech; logged; drain is short |
| R3 | New server fails to start after the old one quit | Low | Medium | Same start path and error as today (`server.log`) |
| R4 | A release forgets to bump the version | Low | Low | Release checklist already bumps `plugin.json` |

## Implementation outline (detailed in S2)

1. Server: read the version; `/health` returns it; `/quit` marks the server quitting; exit as soon as
   it is not busy; 503 for new speech while quitting.
2. Client: read the version; `ensure_server()` compares, sends `/quit` to an older server, waits for
   the socket to go, then starts the new one under `server.lock`; `status` prints the version.
3. Tests: version compare, `/quit` on an idle and a busy server, 503 while quitting, the client
   restart path with a fake server.
4. Docs: CLAUDE.md, README fork section, update block note.
