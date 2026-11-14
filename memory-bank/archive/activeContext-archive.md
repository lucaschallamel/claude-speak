# Active context archive

**Purpose**: session blocks rolled out of [activeContext.md](../activeContext.md), newest first,
moved verbatim. Not part of the session-start read; consult on demand.

## Session 2026-11-14: COPPER setup

- **Focus**: enable the COPPER harness on this repository.
- **Delivered**: COPPER rules (`.claude/rules/cu/`, user profile filled), pre-push guard, this
  memory bank, `docs/dev-journal/`, `docs/ROADMAP.md`, a Kanban board and one story file per open
  issue in `docs/roadmap/backlog/`.
- **Decisions**: commit COPPER files in the repository; full story files named by GitHub issue
  number (`US-002` = issue #2); the GitHub issue stays the tracker, the story file holds the spec.

## Session 2026-11-13: #2 and #3

- **Delivered**: the server polls the dictation state file every 100 ms and stops speech when it
  leaves `idle` (`CLAUDE_SPEAK_DICTATION_STATE`, voxtype default). `UserPromptSubmit` posts `/stop`
  with the session id and touches `hush-<session>`, so a summary still being written is dropped.
- **Learnings**: an empty state-file read is a half-done write, not idle (double stop on macOS CI).
  `gh pr create` in a fork targets upstream: always pass `--repo lucaschallamel/claude-speak`.
