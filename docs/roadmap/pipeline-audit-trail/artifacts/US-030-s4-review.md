# US-030 S4 Code Review: Restart a stale server after a plugin update

**Date**: 2026-11-19 | **Profile**: standard | **Story**:
[US-030](../../backlog/US-030-restart-a-stale-server-after-a.md) (issue #30)

**Purpose**: S4 findings, their dispositions and the fixes.
**Audience**: Lucas, the S5 and S7 reviewers.

## Review

- **Reviewed commit**: `f92e345d3bc82c64451ccf5fdaf08d95eeb38fb4`
- **Fresh reviewer**: general-purpose subagent. Inputs: `commands/quality-review.md`,
  `fresh-context-review.md`, the story file, `git diff main...f92e345`, and the code and tests it
  touches. Not given: the build conversation, the S1/S2 artefacts, the author's self-review.
  Verdict dictated: no. It ran the 126 tests (OK).
- **Author pass**: confirmed findings 1, 2 and 4 on the code; found nothing further.
- **Overall Status**: PASS (no Critical or High).
- **Disposition (Lucas, 2026-11-19)**: "review, assess, mitigate all issues, findings and risks, if
  any, with precision and care": every finding mitigated.

## Findings and mitigations

| # | Severity | Source | Issue | Mitigation | Test |
| - | -------- | ------ | ----- | ---------- | ---- |
| 1 | Low | fresh, author | With `uv` missing from a hook's PATH, a stale server made `ensure_server` raise instead of speaking through it. | No `uv`: the server found is returned as it is; with no server at all, the error stays. | `test_no_uv_keeps_using_the_old_server` |
| 2 | Low | fresh, author | One failed `/health` (2 s timeout) counted as "gone", so a loaded machine could start a second server too early and drop the speech. | "Gone" needs two failed health checks in a row. | `test_one_slow_health_check_is_not_gone` |
| 3 | Low | fresh | A `/speak` passing the handler's quit check just before `watch_idle` decided to exit got 202 and was never spoken. | `watch_idle` decides and sets `Speaker.closed` under `state_lock`; `speak` and `replay` raise `Closed` once it is set; the handler answers 503. Also closes the same window on the plain idle exit, which predates this story. | `test_a_closed_speaker_refuses_speech_and_replay`, `test_speech_that_raced_the_exit_is_refused_not_lost`, `test_quit_on_a_busy_server_waits_for_its_speech` (checks `closed`) |
| 4 | Low | fresh, author | A 503 was dropped with no trace on the client; a client of the same version as a draining server sent it speech it would refuse. | A server already `quitting` is waited for like a stale one, whatever its version, without a second `/quit`; a remaining 503 is logged to `claude-speak.log`. | `test_server_already_quitting_is_waited_for_without_a_second_quit`, `test_speech_refused_by_an_exiting_server_is_logged` |
| 5 | Low | fresh | After a 120 s overrun, every worker queued on `server.lock` waited another 120 s. | An overrun touches `retire-overran` in the data dir; for the next `RETIRE_WAIT` seconds `_retire` returns at once. | `test_after_an_overrun_queued_workers_do_not_wait_again`, `test_drain_past_the_wait_is_logged_and_nothing_starts` |
| 6 | Info | fresh | AC1 needs the version to be 0.5.0; `plugin.json` says 0.4.0. | Story "Release" section: the 0.5.0 release PR bumps it (the existing release rule). | n/a |
| 7 | Info | fresh | `plugin_version` duplicated in client and server. | Kept on purpose; each docstring names its twin and why (the server is a standalone uv script). | existing manifest tests on both sides |
| 8 | Info | fresh | No test for `/quit` raising OSError. | Added. | `test_quit_that_cannot_be_sent_uses_the_old_server` |
| 9 | Info | fresh | Two `if health:` blocks in a row in `cmd_status`. | Merged. | n/a |

## Verification after the fixes

- `python3 -m unittest discover tests`: 134 tests OK; the timing-sensitive classes (WatchIdleTest,
  QuitTest, EnsureServerTest) passed five runs in a row.
- `uvx ruff check scripts tests`: 29 findings, the same set as `main`.
- The fixes change code after the reviewed commit; S5 reviews the new head.

## Second pass: ponytail review of `main...29aa4f1` (2026-11-19)

Lucas ran `/ponytail:ponytail-review` on the branch after the S4 fixes, then asked again for every
finding to be mitigated. Author review in the same session, so it is not independent; S5 reviews the
result fresh.

| # | Group | Issue | Mitigation | Test |
| - | ----- | ----- | ---------- | ---- |
| P1 | Should fix | Speech reaching the server in the ~0.5 s that `shutdown()` takes after an idle exit, or a same-version client hitting a draining server, got 503 and was dropped; `/health` still said `quitting: false`, so a retry could not help. | `/health` reports `quitting` when the speaker is closed too; `send_to_server` retries a 503 once through `ensure_server()`, which waits for the quitting server and starts a new one, with the same body and hook time; only a second 503 is logged. | `test_health_says_quitting_once_an_idle_exit_has_begun`, `test_speech_refused_once_is_sent_again_to_the_new_server`, `test_speech_refused_twice_is_logged` |
| P2 | Nice to have | The quitting rule was written twice: a handler pre-check with its own message, and `Closed` from the speaker. | `/quit` calls `Speaker.close()` (under `state_lock`); `speak`, `replay` and now `warm` raise `Closed`; one 503 path and message (`quitting`) in the handler. The handler branch is gone. | `test_quitting_server_refuses_new_speech_but_still_stops` (now against a real queue-only Speaker, queue checked empty), `test_health_reports_version_and_quitting` (checks `closed`) |

After the second pass: 135 tests OK; the timing-sensitive classes passed five runs in a row; ruff 29,
the `main` baseline.
