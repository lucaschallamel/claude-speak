# Tech context

**Last Updated**: 2026-11-14

**Purpose**: stack, setup and tools. Commands are in [CLAUDE.md](../CLAUDE.md) (Commands).

## Stack

- Python 3.10+. Client: stdlib only. Server: PEP 723 script (`kokoro-onnx`, `numpy`) run by `uv`.
- Kokoro-82M ONNX; voices are 54 style vectors (`[lang][gender]_name`, e.g. `bm_george`).
- Players: `pw-play`, `paplay`, `aplay`, `afplay`, or `CLAUDE_SPEAK_PLAYER`.

## Tests and CI

- `python3 -m unittest discover tests`: no model, audio or network; server deps stubbed.
  Tests that drive `Speaker._run` for real need numpy and are skipped in CI (`skipIf` on the stub);
  they run on any machine with numpy (omarchy has it).
- To run the suite as CI does, block the deps: `sys.modules["numpy"] = None` (and `kokoro_onnx`)
  before `unittest` discovery.
- `.github/workflows/tests.yml`: Linux and macOS × Python 3.10 and 3.13; `main` requires all four.
- Real-audio checks: run the worktree's server with its own `CLAUDE_SPEAK_DATA` (models symlinked
  from the installed data dir) and `CLAUDE_SPEAK_PLAYER` set to a logging script or `avatar-play`,
  so the installed plugin is untouched. Coverage when needed: `uvx --with numpy coverage run`.
- Hotkeys: `~/.local/bin/claude-speak` is the README wrapper (newest installed version, plugin data
  dir); SUPER+Escape stop and SUPER+SHIFT+Escape replay are bound in `~/.config/hypr/bindings.lua`.

## Install

The installed plugin comes from GitHub, not the working copy: push, bump `plugin.json` version,
then `claude plugin marketplace update claude-speak` and `claude plugin update
claude-speak@claude-speak`, then restart. `claude --plugin-dir .` runs the working copy.

## Known constraints

- `claude plugin validate .` fails: the name `claude-speak` is reserved. It predates the fork;
  install and update still work. A rename is an open decision.

## Tools

- GitHub issues and milestones; COPPER story files mirror them ([docs/ROADMAP.md](../docs/ROADMAP.md)).
- Serena MCP (`.serena/`), Hindsight bank `proj-claude-speak`, Orca worktrees, COPPER rules and
  pre-push guard.
