# US-030 S2 Plan: Restart a stale server after a plugin update

**Date**: 2026-11-19 | **Profile**: standard | **Story**:
[US-030](../../backlog/US-030-restart-a-stale-server-after-a.md) (issue #30) | **Input**:
[S1 kickoff](US-030-s1-kickoff.md)

**Purpose**: how S3 builds US-030, the options rejected, and what could go wrong.
**Audience**: Lucas, the S4/S5 reviewers and the agent running the pipeline.

## Approach

### Server (`scripts/server.py`)

1. `plugin_version()` reads `version` from `../.claude-plugin/plugin.json` next to the script; `""`
   when the file is missing or unreadable. Read once at start into `VERSION`.
2. `Server` gains `quit`, a `threading.Event`.
3. `GET /health` adds `"version": VERSION` and `"quitting": server.quit.is_set()`.
4. `POST /quit` sets `server.quit` and answers 202. It never touches the speaker.
5. While `server.quit` is set, `/speak`, `/replay` and `/warm` answer 503
   (`{"error": "quitting for a newer version"}`) and log it. `/stop`, `/synth` and `/health` still work.
6. The idle watcher moves to a module-level `watch_idle(server, speaker, idle_timeout)` so tests can
   drive it. It waits on `server.quit` with a 15 s timeout instead of sleeping, so `/quit` wakes it at
   once. It exits when the speaker is not busy (`time.time() > speaker.busy_until`, which already
   covers queued and playing speech) and either the server is quitting or it has been idle past the
   timeout. While quitting and busy it re-checks every 0.2 s.

### Client (`scripts/claude_speak.py`)

1. `VERSION` read the same way from `ROOT / ".claude-plugin" / "plugin.json"` (stdlib `json`).
2. `_version_tuple(v)` turns `"0.10.2"` into `(0, 10, 2)`; anything unparseable, or missing, is `()`,
   which sorts below every real version.
3. `_stale(health)` is true only when the server's version is lower than the client's (AC4). An
   unparseable client version is never stale-checking anything, so a broken checkout cannot start a
   restart loop.
4. `ensure_server()`: the first health check returns at once unless the server is stale. Under
   `server.lock` the second check calls `_retire(data, health)` for a stale server, then starts the
   new server as today.
5. `_retire()` posts `/quit`. If the server does not answer 202 (a server from before this story),
   it returns the health as it is and the old server is used at once, with no wait (decision 1). Else
   it polls `server_health()` every 0.5 s until the socket stops answering, up to `RETIRE_WAIT = 120`
   s, and returns `None` so the new server starts.
6. `cmd_status` prints `version:` for a running server, and `(quitting)` when it is draining.

### Tests

- Server: `plugin_version()` on a real and a missing file; `/health` carries `version` and
  `quitting`; `/quit` answers 202 and sets the event; `/speak` answers 503 while quitting and does not
  reach the speaker; `watch_idle` exits at once when quitting and idle, and waits while busy, exiting
  once `busy_until` passes (AC2, AC3).
- Client: `_version_tuple` and `_stale` (older, same, newer, missing, two-digit parts); `ensure_server`
  with a same-version server (no `/quit`, no start), a newer server (no `/quit`, AC4), an older server
  (`/quit`, wait, start), a server refusing `/quit` (used at once, no start), and a drain past
  `RETIRE_WAIT` (logged, no start). `request`, `server_health` and `subprocess.Popen` are mocked, as
  the existing tests do.

### Docs

CLAUDE.md architecture paragraph (`/quit`, version check), README fork section, the server's
endpoint docstring.

### Hands-on (S6)

A worktree server with its own `CLAUDE_SPEAK_DATA`: start it from a copy whose `plugin.json` says
`0.4.9`, queue a long reply, then speak from the worktree (`0.5.0` in a scratch copy of
`plugin.json`, never committed). Check: the reply finishes (AC2), the new server answers with the new
version (AC1), the gap between the last chunk and the new speech, and that a `0.4.9` client leaves a
`0.5.0` server alone (AC4).

## Alternatives considered

| Option | Why not |
| ------ | ------- |
| Compare the server script's path instead of a version | No notion of newer, so two sessions on two versions would ping-pong; a worktree sharing the data dir would restart the installed server. |
| One socket per version (the version in `socket_path`) | No quit needed, but old and new servers would both play at once during the overlap, which breaks lanes and replay. |
| Kill the old server by PID (SO_PEERCRED / LOCAL_PEERPID) | Lucas chose one last manual step instead (S1 decision 1). |
| Compare versions for any difference, not "older" | Two sessions on different versions restart each other forever (S1 challenge 2). |

## Deviation from S1

S1 decision 4 said that past 120 s the client "speaks through the old server". A quitting server
refuses new speech with 503, so that fallback cannot speak. Corrected: past 120 s the client logs
`old server still draining after 120 s; speech dropped` to `claude-speak.log` and gives up on that
one utterance. The next speech tries again. This needs 120 s of queued speech, which lanes and the
per-session replacement make rare. The story file is updated to match.

## What could go wrong

| Risk | Effect | Guard |
| ---- | ------ | ----- |
| The release forgets to bump `plugin.json` | No restart; old code keeps running | Release checklist already bumps it; `status` shows the version |
| `server.shutdown()` called while a handler thread is answering | Response cut | `shutdown` only stops `serve_forever`; `daemon_threads` finish; same as the idle exit today |
| New server fails to start after the old one quit | Silence until the next speech | Same error path as today: `RuntimeError`, `server.log` |
| `/health` slow while the old server synthesises | `_retire` sees `None` early and starts a second server | The new server checks `socket_in_use` and exits "already running"; the client keeps polling until health answers or `wait` ends |
| Test of `watch_idle` flaky on timing | Red CI | Drive it with short timeouts and a fake speaker; assert on the event, not on wall time |
| Client version unreadable in a broken checkout | Unwanted restarts | Unparseable client version disables the check |
