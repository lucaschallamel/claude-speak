# US-031 S1 Kickoff: Settings drift test

**Date**: 2026-11-20 | **Profile**: lightweight | **Story**:
[US-031](../../backlog/US-031-settings-drift-test.md) (issue #31)

**Purpose**: S1 review of US-031 (scope, ACs, feasibility, risks) and the input to the S2 plan.
**Audience**: Lucas and the agent running the pipeline.

Issue #31 was re-read on 2026-11-20 and has no comments, so the story file held everything known.

## Findings from the code

- **The four places today.** `DEFAULTS` (`scripts/claude_speak.py:117`) and `userConfig`
  (`.claude-plugin/plugin.json`) both hold `auto_speak`, `summarize`, `voice`, `speed` and
  `summary_model`, with equal default values (`True`, `True`, `af_heart`, `1.1`, `haiku`).
  `OVERRIDABLE` (`scripts/claude_speak.py:109`) holds `auto_speak`, `summarize`, `voice`, `speed`.
- **The skill names flags, not keys.** `skills/speak-settings/SKILL.md` saves answers with
  `config --voice … --speed … --auto … --summarize …`. The literal key `auto_speak` does not appear
  in it, so the story's third check ("every `OVERRIDABLE` key is named in the skill") fails on main
  as written. `auto_speak` maps to `--auto`; the other three map to `--<key>` with dashes.
- **The `config` parser is built inside `main()`** (`scripts/claude_speak.py:969`), so a test
  cannot read its flags without running the CLI. The test checks the skill text, which is where a
  forgotten flag would break the menu.
- **Existing tests.** `tests/test_client.py` already has `SettingsTest`; no test reads
  `plugin.json` `userConfig` or the skill. The new test fits there as one class, stdlib only, no
  model, audio or network.

## Decisions (Lucas, 2026-11-20, via AskUserQuestion)

1. **Skill check maps key to flag.** The test derives each `OVERRIDABLE` key's flag as
   `--` + key with dashes, with one exception held in the test: `auto_speak` -> `--auto`. No change
   to the skill or the runtime.
2. **Default values are compared too.** Each `DEFAULTS` value must equal the `default` in
   `userConfig`. It catches a default changed in one place only, the same kind of drift.

## Implementation plan (input to S2)

- [ ] Add `SettingsDriftTest` to `tests/test_client.py`: keys equal, values equal, `OVERRIDABLE`
      subset of `DEFAULTS`, each `OVERRIDABLE` flag present in the skill.
- [ ] Prove AC1 by mutation at S3: add a dummy key to each place in turn and record that the test
      fails each time, then revert.
- [ ] Update `CLAUDE.md` "Settings precedence" to say the test enforces the rule.
- Effort: under an hour. Points stay at 1.

## Risks

- **Not covered on purpose:** `cmd_config` lists the four overridable keys by hand twice (the
  parse loop at line 874 and the "current settings" listing at line 890), and `with_voice()` adds
  per-call flags. A new overridable key missing there is not caught. Out of scope; the skill check
  forces a `config` flag to exist, since the skill would otherwise call an unknown flag.
- **False failure on a legitimate exception:** a future key that is deliberately not in
  `userConfig` (internal-only) would fail the test. Then the test gets an explicit exception list,
  decided in that story.

## Challenge Log

**Story**: US-031 | **Profile**: lightweight | **Entries**: 4

| #   | Aspect               | Challenge                                                                                        | Disposition                                                                                                         | Status   |
| --- | -------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- | -------- |
| 1   | Scope stress-test    | The third check, as written, fails on main: the skill names `--auto`, never `auto_speak`.        | Lucas: map key to flag in the test (`auto_speak` -> `--auto`), no skill change. Story requirements updated.         | resolved |
| 2   | AC testability       | How is "fails when a setting is added to only one place" shown, not just claimed?                 | S3 mutation run: a dummy key added to each of the four places in turn, test fails each time; output in S3 evidence. | resolved |
| 3   | Risk surfacing       | Keys equal but defaults differ (e.g. speed 1.1 in one place, 1.0 in the other) passes unseen.     | Lucas: compare default values as well. Added to AC1 and requirements.                                               | resolved |
| 4   | Dependency freshness | Must land before US-009 and US-032, which add settings; is main current and the test upstreamable? | Branch cut from main 88bc8dd (current). Test is stdlib `unittest` in the existing file, so it can go upstream.      | resolved |
