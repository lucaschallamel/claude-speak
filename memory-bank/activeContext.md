# Active context

**Last Updated**: 2026-11-20

**Purpose**: the current focus. Rolling: keep the last one or two sessions, move older ones to
[archive/](archive/activeContext-archive.md).

## Current phase

Milestone 2 Quiet shipped as v0.4.0 (2026-11-15). Backlog reviewed on 2026-11-16: milestone 4
"Smarter speech" comes next (release 0.5.0), then milestone 3 "Characters"; order in
`docs/ROADMAP.md`. Milestone 3 Smarter speech started with US-030 (2026-11-19/20), then US-031 (2026-11-20).

## Session 2026-11-20: US-031 , settings drift test

- **Focus**: fourth story through `/cu:pipe` (lightweight profile), S0-S8 in the Orca worktree
  `US-031-settings-drift-test`, branch `lucaschallamel/US-031-settings-drift-test`. Three fresh
  reviews (S4, S5, S7) and one ponytail review; every finding mitigated at Lucas's request.
- **Delivered**: `SettingsDriftTest` in `tests/test_client.py`, five tests: keys equal between
  `DEFAULTS` and `userConfig`; default values equal (a bool stays a bool); `OVERRIDABLE` a subset
  of `DEFAULTS`; each `OVERRIDABLE` flag in the real `config` parser (read through `config --help`)
  and on a `claude-speak config` line of the skill; every skill flag known to the parser. No
  runtime change. `CLAUDE.md` names the test and its limits. 147 tests.
- **Key decisions**: map key to flag in the test (`auto_speak` -> `--auto`), no skill edit;
  compare default values; S5 records "no trust boundary touched"; the `cmd_config` gap stays a
  note; upstream in the later batch, no version bump (Lucas, S1 and after S3).
- **Learnings**: `config` uses `parse_known_args`, so a flag the parser lacks is dropped with no
  error: drift there is silent data loss. Mutations in a scratch copy make AC evidence cheap and
  repeatable. The push guard refuses a push without a named branch, and also any shell command
  whose text merely mentions the push subcommand; name the branch, and keep such text in files.
- **Journal**: [2026-11-20-us-031-settings-drift-test](../docs/dev-journal/2026/11/2026-11-20-us-031-settings-drift-test.md)

## Next steps

- [ ] 0.5.0 release (end of milestone 3): bump `plugin.json`, keep `pkill` once in the update
      block for the 0.4.x server, then `claude-speak status` across a real 0.5.0 to 0.5.x update.
- [x] US-031: merged as PR #43 (de4a0ee), CI 4/4 green; closed.
- [ ] Then US-006 (measure the Notification delay at S1).
- [ ] Laptops: Lucas runs the 0.4.0 update block on each when he is on it.
- [ ] From now on: `in progress` label at S0 (removed by the close PR); re-estimate points at S1.
