# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Claude Code plugin that speaks a short summary of each Claude reply using Kokoro-82M, a local TTS model. This repo is the `lucaschallamel/claude-speak` fork of `kyleoliveiro/claude-speak`. The fork adds 20-word one-sentence summaries, spoken `AskUserQuestion` prompts, mid-turn interjections and `[mood gesture]` avatar cues. The "Fork additions" section at the end of `README.md` lists them. Keep fork changes small so upstream merges stay easy.

## Commands

No build step or linter config. Tests are stdlib `unittest` and need no model, audio or network. `server.py`'s numpy and kokoro_onnx are stubbed when not installed. CI (`.github/workflows/tests.yml`) runs them on Linux and macOS.

```bash
python3 -m unittest discover tests                                   # all tests
python3 -m unittest tests.test_client.SpeakableTest.test_links_and_urls   # one test
claude --plugin-dir .            # run Claude Code with this working copy as the plugin
claude plugin validate .         # check .claude-plugin/ manifests
CLAUDE_SPEAK_DATA=/tmp/claude-speak ./bin/claude-speak say "hello"   # test the voice directly
./bin/claude-speak status        # server, player and settings
./bin/claude-speak stop
# simulate a hook event:
echo '{"hook_event_name":"Stop","session_id":"x","transcript_path":"/path/to.jsonl","cwd":"'"$PWD"'"}' \
  | CLAUDE_SPEAK_DATA=/tmp/claude-speak ./bin/claude-speak hook
```

Errors from detached runs go to `claude-speak.log` in the data dir; the server writes `server.log`. Installed data dir: `~/.claude/plugins/data/claude-speak-claude-speak/`.

## Project memory and backlog (COPPER)

- Read the six files in `memory-bank/` at session start. Update `activeContext.md` and `progress.md` when work lands.
- Roadmap: `docs/ROADMAP.md`. Story specs: `docs/roadmap/backlog/`, one file per GitHub issue, numbered by the issue (`US-004` = #4). Board: `docs/roadmap/KANBAN.md`. Keep issue, story file and card in step.
- Session notes: `docs/dev-journal/YYYY/MM/`.
- COPPER rules: `.claude/rules/cu/`, managed by `cu-rules`. Only `00-the-user.rules.md` is edited by hand.
- PRs and issues: always pass `--repo lucaschallamel/claude-speak`, because `gh` defaults to upstream in this fork.

## Architecture

Two processes:

- **Client** `scripts/claude_speak.py`: **stdlib only**. Hooks must start fast, so never add a dependency here. `bin/claude-speak` runs it with `python3`, or with `uv` as a fallback. It holds every subcommand: `hook`, `speak`, `rephrase`, `auto`, `config`, `say`, `stop`, `again`, `status`, `setup` and internal `_worker`.
- **Server** `scripts/server.py`: a PEP 723 inline-deps script (`kokoro-onnx`, `numpy`) run with `uv run --script`. It keeps the model loaded and serves HTTP on a Unix socket in the data dir (`/health`, `/speak`, `/warm`, `/synth`, `/stop`, `/replay`, `/quit`). It downloads the model on first start, then plays chunk by chunk through `pw-play`/`paplay`/`aplay`/`afplay`. Speech is queued per session: a newer `/speak` from the same session replaces the older one. `/speak` takes `priority` (`urgent` for questions, `normal` for replies, `low` for status lines; set per hook event by the client) and `at`, the hook time. Lanes play in that order, after any replay. Another session's higher lane cuts a status line at once and a reply at its next chunk; the reply stops synthesising ahead, the waiting job's first chunk is made meanwhile (`_prefetch`), and the reply resumes from its first unplayed chunk. A status line not started 5 s after `at` is dropped (`STALE_LOW`, in both client and server). `split_chunks` cuts all speech into chunks of about `CHUNK_CHARS` (80): sentences, long ones split at commas and semicolons. Keep chunks small: Kokoro synthesis can't be interrupted, so preempting speech waits for the chunk in flight, and over a reply for the chunk playing. The server exits after `CLAUDE_SPEAK_IDLE_TIMEOUT` idle seconds (`watch_idle`). `ensure_server()` in the client starts it on demand. Both processes read `version` from `.claude-plugin/plugin.json`; `/health` reports the server's. When the server is older than the client (`_stale`; never for the same or a newer version, so two sessions on two versions don't fight), `ensure_server()` posts `/quit` under `server.lock` and waits up to `RETIRE_WAIT` (120 s) for it to go. A quitting server finishes its queue, answers new `/speak`, `/replay` and `/warm` with 503, then exits. A server that refuses `/quit` (before 0.5.0) is used as it is.

Hook flow (`hooks/hooks.json`, all routed to `claude-speak hook`, dispatched on `hook_event_name` in `cmd_hook`):

- `SessionStart` only records the session's transcript path, so skills can find it later.
- `Stop` takes the reply from `last_assistant_message`, or from the transcript tail. It hands the text to `spawn_worker()`, a detached `_worker` process, so the hook returns in about 50 ms.
- `PreToolUse` (`AskUserQuestion`) speaks the question, because `Stop` does not fire until the user answers.
- `PostToolUse` (`*`) calls `maybe_interject`: it speaks the latest mid-turn status line, at most every `INTERJECT_GAP` seconds.
- The worker calls `prepare()`. Replies longer than `SUMMARY_THRESHOLD` are summarized by `_ask_claude()`, a nested `claude -p` with no tools, no MCP and no thinking. The summary is cached per session for 7 days. A leading `[mood gesture]` cue is stripped and posted to `CLAUDE_SPEAK_AVATAR_URL/cue`. The rest goes to the server.

Invariants that are easy to break:

- **Recursion guard:** `_ask_claude` sets `CLAUDE_SPEAK_NESTED=1`, and `cmd_hook` returns at once when it sees it. Headless runs (`CLAUDE_CODE_ENTRYPOINT=sdk*`) are skipped unless `CLAUDE_SPEAK_HEADLESS=1`.
- **No double speech:** `/speak` writes a `skip-<session>` marker, so the next `Stop` does not speak the skill's reply again. `is_own_reply()` filters replies that start with `🔊`, `claude-speak:` or `No change.`. Skill replies must keep those prefixes.
- **Settings precedence** (`load_settings`): `DEFAULTS`, then `options.json`, then `CLAUDE_PLUGIN_OPTION_*` env, then `overrides.json`, then explicit flags. Skills do not receive `CLAUDE_PLUGIN_OPTION_*`, so hooks copy them into `options.json` (`save_options`). Only keys in `OVERRIDABLE` go into `overrides.json`. A new setting must be added to `DEFAULTS`, `userConfig` in `.claude-plugin/plugin.json` and, if user-toggleable, `OVERRIDABLE` and the `speak-settings` skill.

Skills (`skills/*/SKILL.md`) are thin. Most run the CLI through a `` !`…` `` preprocessor line and only echo its status line. They use `disable-model-invocation: true` and an `allowed-tools` limited to `Bash(${CLAUDE_PLUGIN_ROOT}/bin/claude-speak *)`.

Summary wording is set by `SUMMARY_PROMPT` and `REPHRASE_PROMPT` near the top of `claude_speak.py`. The allowed avatar cue values are `AVATAR_MOODS` and `AVATAR_GESTURES`.

Release: bump `version` in `.claude-plugin/plugin.json`.

`assets/` holds generators for the README header, banner and promo video (`make_*.py`). They are not part of the runtime.
