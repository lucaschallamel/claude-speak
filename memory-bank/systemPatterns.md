# System patterns

**Last Updated**: 2026-11-15

**Purpose**: architecture and the patterns that must hold. The full map is in
[CLAUDE.md](../CLAUDE.md) (Architecture); this file records only what CLAUDE.md does not.

## Architecture in one line

Hooks call a stdlib client (`scripts/claude_speak.py`), which detaches a worker, summarises with a
nested `claude -p`, and sends text to a Kokoro server (`scripts/server.py`) on a Unix socket. The
server queues speech by lane (replay, urgent, normal, low) and per session, and plays it chunk by
chunk through a player command, which agent-avatar replaces.

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
  being synthesised. Covered by `ReplayTest` in `tests/test_server.py`. US-005 added the
  preemption checks (`job.preempt`), the `played` count, the resume re-queue on the break path
  (also when the producer stopped early with nothing queued), and `_audio`'s stop-ahead on
  preempt and wait for a prefetch; covered by `LanesTest`.
- `Speaker.speak` and `Speaker._loop` in `scripts/server.py` (US-005): `speak` inserts by lane
  (`_enqueue`) instead of appending, drops a status line that would replace its session's question
  or reply, and preempts another session's lower-lane speech (`_preempt_for`, which also hands
  the next question's first chunk to a single `_prefetch` worker). `_loop` picks jobs
  through `_next`, which drops stale status lines.
- `split_chunks` and `CHUNK_CHARS` in `scripts/server.py` (US-005): chunks went from 250 to about
  80 characters, split at sentences and, inside long sentences, at commas and semicolons (no
  longer at colons); the packing loop moved into `_pack`. Covered by `SplitChunksTest`.
- `Server.__init__` in `scripts/server.py` (US-004): binds the socket under umask `0o177`, so only
  the user can connect even when it falls back to a shared `/tmp`.

## Anti-patterns

- A dependency in the client.
- Speaking our own skill replies (keep the `🔊`, `claude-speak:` and `No change.` prefixes).
- Settings outside the precedence chain (`load_settings`).
- Large speech chunks: Kokoro synthesis can't be interrupted, so preempting speech waits for the
  chunk in flight and, over a reply, for the chunk playing (US-005: 250-char chunks meant a 15 s
  wait). Keep `CHUNK_CHARS` small.
- Trusting latency numbers taken under load: check the load average first and record it with every
  measurement set (US-005: the same code measured 0.7-9.6 s at load 13-18).

## Decisions

Settled design decisions live as comments on the GitHub issues; read the thread before building.
