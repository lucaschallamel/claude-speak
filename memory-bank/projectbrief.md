# Project brief

**Last Updated**: 2026-11-14

**Purpose**: the foundation of claude-speak (fork): goals, scope and constraints. Read with the
other five core files at every session start ([Rule 03](../.claude/rules/cu/03-memory-bank.rules.md)).

## Project

claude-speak, Lucas Challamel's fork (`lucaschallamel/claude-speak`) of `kyleoliveiro/claude-speak`.
A Claude Code plugin that speaks a short summary of each Claude reply with Kokoro-82M, a local,
offline TTS model. A sibling project, agent-avatar, plays the audio through an animated avatar.

## Objectives

- A voice partner for Claude Code: short, well-timed spoken summaries that never talk over Lucas.
- Characters: a distinct voice, tone and avatar per Claude session.
- Smarter speech: know what is worth saying and how to say it.

## Scope

- **In**: the plugin (hooks, client, TTS server, skills), its tests and CI, and the hooks
  agent-avatar uses (`CLAUDE_SPEAK_PLAYER`, `CLAUDE_SPEAK_AVATAR_URL`).
- **Out**: agent-avatar's own code (its own repository and backlog); cloud TTS; remote/SSH use.

## Constraints

- The client stays stdlib-only: hooks must start fast.
- Keep fork changes small and additive so upstream merges stay easy.
- Linux (Omarchy) first, without breaking macOS.
- Public repository: nothing private (hosts, email, the private agent-avatar repository URL).

## Success metrics

- The four CI checks stay green (Linux and macOS × Python 3.10 and 3.13).
- Each milestone ships as a tagged release.
