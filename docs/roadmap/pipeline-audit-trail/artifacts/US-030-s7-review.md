# US-030 S7 Critical Review: Restart a stale server after a plugin update

**Date**: 2026-11-20 | **Profile**: standard | **Story**:
[US-030](../../backlog/US-030-restart-a-stale-server-after-a.md) (issue #30)

**Purpose**: Definition of Done verdict, challenge log, findings and their mitigations.
**Audience**: Lucas; the S10 pull request reviewer.

## Review

- **Reviewed commit**: `ef0b279`
- **Fresh reviewer**: general-purpose subagent, read-only. Inputs: `commands/dod-verify.md`, DoD
  Level 1 from `definition-of-done.md`, `fresh-context-review.md`, the story file,
  `git diff main...ef0b279` and the code it touches, `pipeline_validator.py status` output, the
  pipeline YAML and stage artefacts (used only to see the author's claims), `CLAUDE.md`. Verdict
  dictated: no. It ran the 140 tests (OK), ruff 0.15.4 (clean) and coverage.py; it changed no repo
  file.
- **Author pass**: confirmed F1 to F3 on the code. One correction: the HTTP-level `/synth` 503 was
  already tested (`test_quitting_server_refuses_new_speech_but_still_stops`, added at S5). Found one
  pre-existing issue while running the tests: the client never closed its copy of the `server.log`
  handle after starting the server (ResourceWarning in the new EnsureServerTest).
- **Overall Status**: WARN. All four ACs pass; no FAIL.
- **Disposition (Lucas, 2026-11-20)**: "review, assess, mitigate all issues, findings and risks, if
  any, with precision and care".

## Criteria (summary)

| Area | Result |
| ---- | ------ |
| AC1a, AC1b, AC2 (bounded by the drain cap), AC3, AC4 | PASS |
| Code quality: CA, SF, RP, REH, IV | PASS; DRY WARN (twin `plugin_version`, deliberate and documented) |
| Tests: all pass, edge cases, test names | PASS; coverage WARN (changed lines mostly covered; `claude_speak.py` as a whole at 57% from older untested code); integration WARN (real-hardware run at S6, not automated) |
| Docs: README, CLAUDE.md, comments | PASS; API docstring and story spec WARN (F1, F2) |
| Code review, lint, security, performance | PASS |
| Version control and pipeline state | PASS |
| Version bump, CHANGELOG, principle tags, S8 capture, PR | SKIP: release per milestone by the maintainer; no CHANGELOG in the repo; tags not a project convention; S8 and S10 come later |

## Challenge log

| # | Perspective | Challenge | Assessment | Severity |
| - | ----------- | --------- | ---------- | -------- |
| 1 | User updating the plugin | Will the next reply go silent or be very late after an update? | Delayed, not lost: drain then model load (29 s at S6); workers are detached, so Claude Code never blocks. | Info |
| 2 | User | Will two sessions on two versions fight? | No: only an older server is replaced (AC4). | Info |
| 3 | User | Will a long queue be cut by the 100 s cap? | Only an old server's queue longer than 100 s. Now stated in AC2, the requirements and the README (F1). | Low |
| 4 | User still on 0.4.x | Does anything break before the `pkill`? | No; a `/quit` and the lock per utterance until then (F4, accepted at S5). | Low |
| 5 | Maintainer merging upstream | Is the fork diff small enough for easy merges? | About 220 lines in `ensure_server`, `send_to_server`, the handler and `watch_idle`; "could go upstream: yes" would remove the cost. | Low |
| 6 | Maintainer releasing | What if the release is not 0.5.0? | The story Release section requires 0.5.0; merging at 0.4.0 is harmless (an unversioned server is used as is). | Low |
| 7 | Maintainer debugging | Does a dev copy take over the installed server? | Only with the same data dir and a higher version; CLAUDE.md says to use a separate `CLAUDE_SPEAK_DATA`. | Info |

## Findings and mitigations

| # | Severity | Issue | Mitigation | Test |
| - | -------- | ----- | ---------- | ---- |
| F1 | Low | Story spec drift: AC2 and the requirements said speech is never cut; the 503 list named only `/speak` and `/replay`; decision 3 said refused speech is lost. | AC2 and the `/quit` requirement state the 100 s drain cap; the 503 list names `/speak`, `/replay`, `/warm`, `/synth`; decision 3 records the single retry. | n/a (docs) |
| F2 | Low | Server docstring left `/synth` out of the 503 list. | Docstring lists all four and the drain cap. | n/a |
| F3 | Low | No test for the `status` version line; `say --out` had no 503 retry; HTTP `/synth` 503 reported untested. | `say --out` retries a 503 once through `ensure_server()`, like `send_to_server`; CLAUDE.md says so. HTTP `/synth` 503 was already tested (S5). | `test_say_out_refused_once_is_sent_again_to_the_new_server`, `test_status_shows_both_versions_and_quitting` |
| F4 | Low | A pre-0.5.0 server gets a `/quit` and the lock before each utterance. | Accepted at S5 (finding 4): ends at the one-time `pkill`, sub-millisecond. | `test_server_from_before_quit_existed_is_used_at_once` (existing) |
| F5 | Info | The S6 hardware run used scratch scripts that are not in the repo. | Story Release section: after installing 0.5.0 and a later 0.5.x, run `claude-speak status` once to confirm the handoff on a real `claude plugin update`. | n/a |
| F6 | Info | One uncommitted line in the pipeline record. | Committed with this stage. | n/a |
| A1 | Info (pre-existing, author) | The client kept its copy of the `server.log` handle open after starting the server. | `with open(...)` around `Popen`; the server keeps its own descriptor. ResourceWarnings in the test run: 0. | EnsureServerTest start paths |

## Verification after the fixes

- `python3 -m unittest discover tests`: 142 tests OK, no ResourceWarning; 142 run, 9 skipped with
  numpy and kokoro_onnx blocked; timing-sensitive classes five runs in a row OK.
- `uvx ruff@0.15.4 check --no-cache` (defaults) on the four changed Python files and
  `--select E4,E7,E9,F,I` on `scripts/ tests/`: All checks passed!
- Not covered: CI on macOS and Python 3.10 (runs on the pull request at S10).
