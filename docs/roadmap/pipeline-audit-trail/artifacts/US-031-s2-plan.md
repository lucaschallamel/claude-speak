# US-031 S2 Plan: Settings drift test

**Date**: 2026-11-20 | **Profile**: lightweight | **Story**:
[US-031](../../backlog/US-031-settings-drift-test.md) (issue #31) | **Input**:
[S1 kickoff](US-031-s1-kickoff.md)

**Purpose**: how US-031 is built, the alternatives rejected, and what could go wrong.
**Audience**: Lucas and the agent running the pipeline.

## Approach

One class, `SettingsDriftTest(unittest.TestCase)`, in `tests/test_client.py`, after
`SettingsTest`. It reads `.claude-plugin/plugin.json` and `skills/speak-settings/SKILL.md` from
`ROOT` (already defined in the file) and imports `cs.DEFAULTS` and `cs.OVERRIDABLE`. Four tests,
one per rule, so a failure names the rule that broke:

| Test                              | Assertion                                                                                       |
| --------------------------------- | ----------------------------------------------------------------------------------------------- |
| `test_defaults_match_user_config` | `set(cs.DEFAULTS) == set(userConfig)`                                                           |
| `test_default_values_match`       | for each key, `cs.DEFAULTS[key] == userConfig[key]["default"]` (subTest per key)                |
| `test_overridable_are_settings`   | `set(cs.OVERRIDABLE) <= set(cs.DEFAULTS)`                                                       |
| `test_skill_sets_overridable`     | for each key, its flag matches `re.search(flag + r"(?![\w-])", skill)` (subTest per key)        |

The flag is derived as `"--" + FLAGS.get(key, key).replace("_", "-")`, with
`FLAGS = {"auto_speak": "auto"}` as a class attribute and a one-line comment naming why
(`config --auto` predates the key). A failure message names the file to edit, for example
"add 'foo' to userConfig in .claude-plugin/plugin.json".

Then one line in `CLAUDE.md` "Settings precedence": the rule is enforced by `SettingsDriftTest`.

## Steps

- [ ] Write the class (about 30 lines). No new import except `re` (stdlib).
- [ ] Run `python3 -m unittest discover tests`: all pass (142 today, 146 expected; count recorded at S3).
- [ ] Mutation run for AC1, each one reverted after: a key `foo` added to `DEFAULTS` only;
      to `userConfig` only; to `OVERRIDABLE` only (also in `DEFAULTS` and `userConfig`, so only
      the skill check fails); and `speed` default changed to 1.0 in `userConfig` only. Each must
      fail with the expected test named. Output recorded in S3 evidence.
- [ ] `CLAUDE.md` line; story ACs ticked at S3.

## Alternatives considered

1. **Parse the `config` argparse parser instead of the skill text.** It would check the CLI flag
   exists, not that the menu uses it. It also needs `main()` split to expose the parser: a runtime
   change for a test. Rejected.
2. **Move the key-to-flag map into `claude_speak.py`** (for example `FLAGS` beside
   `OVERRIDABLE`) and use it in `cmd_config`. Better single source, but a runtime change and more
   upstream diff, against S1 decision 1. Rejected; noted as a follow-up only if the hand-written
   lists in `cmd_config` ever drift.
3. **A separate `tests/test_settings_drift.py`.** Clean, but a second copy of the `sys.path`
   setup and `ROOT`. The existing file already has both. Rejected.
4. **Plain substring check (`flag in skill`).** `--auto` would also match a later `--autoplay`.
   The negative lookahead costs nothing. Rejected.

## What could go wrong

| Risk                                                                                 | Guard                                                                                                 |
| ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| `speed` compares `1.1` (Python float) with JSON `1.1`: equal, but a future `1` vs `1.0` | `1 == 1.0` is true in Python; bool vs int is the trap (`True == 1`). Compare `type` too for bools.    |
| The test passes without checking anything (empty dicts after a path mistake)          | Assert `userConfig` and `OVERRIDABLE` are non-empty before comparing.                                |
| A developer's `CLAUDE_PLUGIN_OPTION_*` env leaks in                                   | The test reads constants and files only, never `load_settings`; no env involved.                     |
| Mutation run left in the tree                                                         | Mutations made in a scratch copy of the files via `mock.patch.dict` / temp edits, then `git diff` checked clean. |
| Upstream merge friction                                                               | Test-only change in an existing file; no runtime diff.                                               |
