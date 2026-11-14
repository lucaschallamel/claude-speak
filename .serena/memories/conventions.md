# Conventions and workflow

- Story IDs = GitHub issue numbers per repo. COPPER story files reuse the number with a type prefix (`US-004` = #4, `SP-015` = #15). Say "claude-speak #2" vs "agent-avatar #2" when both are in play.
- One Orca worktree + branch + PR per issue (`Closes #n`); after approval: squash-merge, back to main, delete branch and worktree.
- main is protected: the 4 unittest checks must pass (admin bypass for emergencies only).
- Release per milestone: bump `.claude-plugin/plugin.json` version via PR, tag `vX.Y.Z`, close the milestone; installed plugin updates with `claude plugin update`.
- At each milestone start: `git fetch upstream`; merge new upstream work into main through a PR.
- Milestones: 1 Foundation, 2 Quiet, 3 Characters, 4 Smarter speech (agent-avatar has 3 and 4). Build order follows them; #15 (second TTS engine spike) last.
- Source of truth: GitHub issues = tracker and discussion; `docs/roadmap/backlog/<ID>.md` = the spec (copied decisions included); keep issue, story file and `docs/roadmap/KANBAN.md` card in step. Current state: `memory-bank/` (read at session start). Session notes: `docs/dev-journal/`. Serena = code conventions; Hindsight = history/reasons; Claude memory = pointers.
- `gh pr`/`gh issue`: always `--repo lucaschallamel/claude-speak` (gh defaults to upstream).
- Linux/Hyprland-first is fine; never break macOS (CI covers it); document Mac fallback per story.
- Generic features stay free of avatar code (upstream later); fork-only bits (avatar cues, Omarchy triggers) behind env flags or separate files.
- Comments explain why only; style matches surrounding code (section banner comments in claude_speak.py).
- Docs to update when behaviour changes: README (fork additions section), CLAUDE.md, skill files.
