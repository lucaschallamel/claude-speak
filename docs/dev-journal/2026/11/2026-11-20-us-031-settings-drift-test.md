---
entry_date: 2026-11-20
author: 'Lucas Challamel'
focus_area: 'US-031: a unit test that catches settings drift'
status: completed
session_duration: 'one session, 2026-11-20'
tags: [us-031, settings, drift-test, unittest, mutation-testing, cu-pipe, fresh-review]
version: '1.0.0'
last_updated: '2026-11-20'
maintained_by: 'Lucas Challamel'
---

**Session summary**: US-031 added `SettingsDriftTest`, which fails when a setting is added to some
of its places but not all, and three fresh reviews grew it from three checks into five that also
catch flags the CLI would drop without an error.

## Why (High-Level Context)

`CLAUDE.md` says a new setting goes into `DEFAULTS`, `userConfig` in `plugin.json` and, when users
can change it, `OVERRIDABLE` and the `speak-settings` skill. Nothing enforced it. US-009 and
US-032 both add settings next, so the check had to exist first (order from the 2026-11-16 backlog
review). Story: [US-031](../../../roadmap/backlog/US-031-settings-drift-test.md), issue #31.

**Session objectives**:

- A test that passes on main and fails when a setting is in one place only (AC1).
- No runtime change; small enough to go upstream later.

## How (The Journey)

### S1: the story's third check failed on main

The story asked that every `OVERRIDABLE` key be "named in" `SKILL.md`. The skill names `config`
flags, not keys, and `auto_speak` is `--auto`, so a literal check failed before any change. Lucas
chose to map key to flag in the test (one exception, `FLAGS = {"auto_speak": "auto"}`) over
editing the skill, and to compare default values too, not only keys.

### S3: four tests and a mutation run

`SettingsDriftTest` in `tests/test_client.py`: keys equal between `DEFAULTS` and `userConfig`;
default values equal, with a bool kept a bool (`True == 1` in Python); `OVERRIDABLE` a subset of
`DEFAULTS`; each `OVERRIDABLE` flag in the skill. AC1 was shown, not claimed: each mutation ran in a
scratch copy of `scripts/`, `tests/`, `skills/` and `.claude-plugin/`, so the working tree was never
touched. `assertRegex` printed the whole skill on failure, so the checks use
`assertTrue(re.search(...), msg)` for one-line messages.

### What the reviews changed

- **S4 (fresh quality review)**: the flag search read all of `SKILL.md`, so a flag named only in
  prose passed. It now reads only the `claude-speak config` lines. The `CLAUDE.md` sentence claimed
  more than the test checked; it now lists the checks and the blind spot (a key the test cannot
  know should be in `OVERRIDABLE`). A stale `FLAGS` entry now fails.
- **S5 (fresh architecture review)**: the key-to-flag map was hand-written, so a CLI rename went
  unseen. Looking closer, `main()` uses `parse_known_args`: a flag the parser lacks is dropped with
  no error, so a setting would silently not save. The test now reads the real parser through
  `config --help` (patched `sys.argv`, stdout redirected, `SystemExit` suppressed), with no runtime
  change.
- **S7 (fresh DoD review)**: a flag added only to the skill still passed. The fifth test checks
  every flag on a skill `config` line against the parser, closing the other direction of the same
  silent drop.
- **Ponytail review**: one assert that could never fail on its own was removed.

### Principle codes

**[TDT]** the test came from the rule it enforces; **[SF]** one class in the existing file, stdlib
only; **[SCP]** no runtime or skill change; **[TST]** 12 mutations plus a control prove each check
fails for the right reason.

## Final State & Next Steps

- 147 tests pass (Python 3.10 too), ruff 0.15.4 clean. Five drift checks; failure messages name the
  file to edit.
- Not covered, by decision: how `cmd_config` handles each flag after parsing (its hand-written key
  lists) and the per-call flags in `with_voice()`. A key deliberately absent from `userConfig` would
  need an explicit exception, decided by the story that adds it.
- Next: S9 close docs, S10 PR (first CI run, macOS included), then US-006.
- Upstream: in the later batch with US-030 and the Quiet features; no version bump.

## Reflection

- **Went well**: running mutations in a scratch copy made AC1 evidence cheap and repeatable, and
  each review reran them with its own new cases.
- **Learned**: `parse_known_args` turns drift into silent data loss; reading the CLI through
  `--help` checks the real parser without touching runtime code.
- **Could improve**: the story's requirements were written without reading `SKILL.md`; checking
  each requirement against the code at story-writing time would have saved the S1 detour.
