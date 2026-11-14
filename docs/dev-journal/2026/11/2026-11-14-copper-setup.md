---
entry_date: 2026-11-14
author: 'Claude Code'
focus_area: 'tooling'
status: complete
tags: [copper, memory-bank, backlog]
---

## Why

Lucas asked to run claude-speak under the COPPER harness: memory bank, dev journal, roadmap and
backlog, with Serena and Hindsight already in place. Until now the project memory was spread over
Claude auto-memory, Serena memories, Hindsight and GitHub.

## How

- `/cu:init` in quick mode, prefilled from Hindsight: `.claude/rules/cu/` installed (17 rules, cu
  4.2.0) and `00-the-user.rules.md` filled. The repository is public, so the profile holds no email,
  location or private host.
- The COPPER guard hook was installed in `.git/hooks` (local only), on top of branch protection.
- Memory bank: the six core files. They link to `CLAUDE.md` instead of repeating it.
- Backlog: one story file per GitHub issue (all 16, 3 done), generated from the issue bodies.
  "What" and "Why" become the overview, "Done when" becomes acceptance criteria, "How" becomes
  technical requirements, and the decision comments are copied in. Effort S/M/L maps to 2/3/5
  points.

## Decisions

- Commit the COPPER files in the repository. Upstream never touches `memory-bank/`, `docs/` or
  `.claude/`, so merges from upstream stay easy.
- Full story files, not just an index. The story number is the GitHub issue number (`US-002` = #2).
  The issue stays the tracker and discussion; the file is the spec.
- No synthesised "As a / I want" line: the auto-written ones read badly, and the overview already
  says what and why.

## Learnings

- #2 and #3 had been merged on 2026-11-13 from another session. The local `main` was behind, so the
  first draft of the memory bank said "paused before #2". Fetch and compare with `origin/main`
  before writing status.
- The COPPER in-session guard refuses any shell command whose heredoc text mentions pushing; write
  such files with the editor tools instead.

## Next

- [ ] Lucas: review and approve the PR.
- [?] Lucas: rename the plugin or keep the reserved name.
- [ ] #4 replay and hotkeys.
