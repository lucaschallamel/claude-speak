# Active context

**Last Updated**: 2026-11-14

**Purpose**: the current focus. Rolling: keep the last one or two sessions, move older ones to
[archive/](archive/).

## Current phase

Milestone 2 Quiet is half done: #2 barge-in (PR #20) and #3 hush on new prompt (PR #21) merged
on 2026-11-13, unreleased. Left: #4 replay and hotkeys, #5 priority lanes, then release 0.4.0.

## Session 2026-11-13: #2 and #3

- **Delivered**: the server polls the dictation state file every 100 ms and stops speech when it
  leaves `idle` (`CLAUDE_SPEAK_DICTATION_STATE`, voxtype default). `UserPromptSubmit` posts `/stop`
  with the session id and touches `hush-<session>`, so a summary still being written is dropped.
- **Learnings**: an empty state-file read is a half-done write, not idle (double stop on macOS CI).
  `gh pr create` in a fork targets upstream: always pass `--repo lucaschallamel/claude-speak`.

## Session 2026-11-14: COPPER setup

- **Focus**: enable the COPPER harness on this repository.
- **Delivered**: COPPER rules (`.claude/rules/cu/`, user profile filled), pre-push guard, this
  memory bank, `docs/dev-journal/`, `docs/ROADMAP.md`, a Kanban board and one story file per open
  issue in `docs/roadmap/backlog/`.
- **Decisions**: commit COPPER files in the repository; full story files named by GitHub issue
  number (`US-002` = issue #2); the GitHub issue stays the tracker, the story file holds the spec.

## Next steps

- [ ] Lucas: review and approve the COPPER setup PR.
- [?] Lucas: rename the plugin, or keep the reserved name?
- [ ] Next story: #4 (replay and hotkeys), in its own Orca worktree, when Lucas says go.
