# System patterns

**Last Updated**: 2026-11-14

**Purpose**: architecture and the patterns that must hold. The full map is in
[CLAUDE.md](../CLAUDE.md) (Architecture); this file records only what CLAUDE.md does not.

## Architecture in one line

Hooks call a stdlib client (`scripts/claude_speak.py`), which detaches a worker, summarises with a
nested `claude -p`, and sends text to a Kokoro server (`scripts/server.py`) on a Unix socket. The
server queues speech per session and plays it through a player command, which agent-avatar
replaces.

## Patterns

- **Detach early**: hooks return in about 50 ms; real work runs in `_worker`.
- **One queue, per-session replacement**: newer speech from a session replaces its older speech.
- **Additive fork changes**: new behaviour behind settings or env vars; upstream code paths kept.
- **Integration through env**: agent-avatar is reached only through `CLAUDE_SPEAK_PLAYER` and
  `CLAUDE_SPEAK_AVATAR_URL`.

## Fork divergences from upstream code

Places where the fork rewrote upstream code instead of adding to it. Expect merge conflicts here
when pulling upstream; keep the fork's behaviour and re-apply upstream's change on top.

- `Speaker._run` in `scripts/server.py` (US-004): the consumer polls the clip queue every 50 ms,
  returns as soon as its job is cancelled, and a drain thread deletes the cancelled producer's
  leftover files. This lets a replay or newer reply start at once instead of waiting for the chunk
  being synthesised. Covered by `ReplayTest` in `tests/test_server.py`.
- `Server.__init__` in `scripts/server.py` (US-004): binds the socket under umask `0o177`, so only
  the user can connect even when it falls back to a shared `/tmp`.

## Anti-patterns

- A dependency in the client.
- Speaking our own skill replies (keep the `🔊`, `claude-speak:` and `No change.` prefixes).
- Settings outside the precedence chain (`load_settings`).

## Decisions

Settled design decisions live as comments on the GitHub issues; read the thread before building.
