# Active context

**Last Updated**: 2026-11-20

**Purpose**: the current focus. Rolling: keep the last one or two sessions, move older ones to
[archive/](archive/activeContext-archive.md).

## Current phase

Milestone 2 Quiet shipped as v0.4.0 (2026-11-15). Backlog reviewed on 2026-11-16: milestone 4
"Smarter speech" comes next (release 0.5.0), then milestone 3 "Characters"; order in
`docs/ROADMAP.md`. Milestone 3 Smarter speech started with US-030 (2026-11-19/20).

## Session 2026-11-19/20: US-030 , restart a stale server after a plugin update

- **Focus**: third story through the full `/cu:pipe` (standard profile), S0-S10, merged as PR #40 (5eaabfa), in the
  Orca worktree `us-030-stale-server-restart`. Three fresh reviews (S4, S5, S7), one ponytail
  review, and a real-hardware run with scratch plugin copies at five versions.
- **Delivered**: both processes read `version` from `plugin.json`, and `/health` reports
  `version` and `quitting`. The client replaces only an older server: it posts `/quit` under
  `server.lock` and waits up to 120 s (gone = two health misses in a row). A quitting server
  refuses `/speak`, `/replay`, `/warm` and `/synth` with 503, finishes its queue, and exits; after
  `DRAIN_CAP` (100 s) it stops its speech and exits anyway. A 503 is retried once. On exit, the
  socket is removed only if it is still the server's own. `status` shows both versions. 142 tests.
- **Key decisions**: old servers (0.4.x) get no automatic kill; the 0.5.0 update block keeps
  `pkill` once (Lucas, S1). Newer wins. Drain, then refuse. The 120 s wait drops one utterance
  past it. Every review finding was mitigated at Lucas's request ("mitigate all").
- **Learnings**: nest the bounds (server drain cap under client wait); fresh reviewers find race
  windows the author misses; brief read-only reviewers with the exact forbidden git commands; the
  worktree guard refuses git-like text in complex commands, so use Write/Edit or script files.
- **Journal**: [2026-11-20-us-030-stale-server-restart](../docs/dev-journal/2026/11/2026-11-20-us-030-stale-server-restart.md)

## Next steps

- [ ] 0.5.0 release (end of milestone 3): bump `plugin.json`, keep `pkill` once in the update
      block for the 0.4.x server, then `claude-speak status` across a real 0.5.0 to 0.5.x update.
- [ ] Then US-031 (lightweight profile: test only), then US-006 (measure the Notification delay
      at S1).
- [ ] Laptops: Lucas runs the 0.4.0 update block on each when he is on it.
- [ ] From now on: `in progress` label at S0 (removed by the close PR); re-estimate points at S1.
