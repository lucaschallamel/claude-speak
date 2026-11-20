# US-030 S5 Architecture, Security and Compliance Review: Restart a stale server after a plugin update

**Date**: 2026-11-20 | **Profile**: standard | **Story**:
[US-030](../../backlog/US-030-restart-a-stale-server-after-a.md) (issue #30)

**Purpose**: S5 findings, risk register, dispositions and the fixes.
**Audience**: Lucas, the S6 and S7 reviewers.

## Review

- **Reviewed commit**: `7891888de9c6a4b2188e1deb3daa1cf72aeeb993`
- **Fresh reviewer**: general-purpose subagent. Inputs: the arch-review method, the fresh-context
  rules, the story file, `git diff main...7891888`, `CLAUDE.md` and the trust-boundary list read from
  `main`. Not given: the plan, the S4 findings, the build conversation. Verdict dictated: no. It ran
  the 135 tests (OK).
- **Process note**: the reviewer was told to work read-only but ran one `git checkout` of the same
  commit and switched back. Checked afterwards: branch intact, HEAD `7891888`, tree clean.
- **Author pass**: agreed with all nine findings; finding 2 is the only one that can silence every
  session.
- **Overall Status**: PASS (no Critical, High or Medium).
- **Trust boundary**: touched, not security-sensitive. `/quit` is reachable only by the same user
  (the socket is mode 0600, also in the `/tmp` fallback); it parses no new input and grants that
  user nothing they could not already do, such as kill the process. No full security audit needed.
- **Compliance**: no new stored data beyond an empty marker file in the user's own data dir; nothing
  leaves the machine; no new dependency.
- **Disposition (Lucas, 2026-11-20)**: "review, assess, mitigate all issues, findings and risks, if
  any, with precision and care": every finding mitigated or, where no change is warranted, accepted
  with its reason.

## Findings and mitigations

| # | Severity | Issue | Mitigation | Test |
| - | -------- | ----- | ---------- | ---- |
| 1 | Low | `say` and `setup` run in the foreground and can block up to 120 s while an old server drains, with no sign why. | When stderr is a terminal, `_retire` prints "waiting for the old voice server to finish speaking..." before it waits; hooks and detached workers have no terminal and stay silent. README notes the pause. | `test_a_person_waiting_is_told_and_an_old_overrun_marker_is_cleared` |
| 2 | Low | A hung player kept a quitting server alive, so every session went silent until `claude-speak stop`. | `watch_idle` caps the drain at `DRAIN_CAP` (100 s): it calls `speaker.stop()` and exits. The cap is below the client's `RETIRE_WAIT` (120 s), so the waiting client sees the server go and starts the new one instead of dropping the speech. The client's overrun log line now names `claude-speak stop`. | `test_a_drain_past_the_cap_stops_the_speech_and_exits` |
| 3 | Low | A working copy run with `--plugin-dir` and a bumped version retired the installed server; other sessions then spoke through dev code. | `CLAUDE.md`: dev runs get their own `CLAUDE_SPEAK_DATA` (the socket is keyed by the data dir); the `--plugin-dir` command line now shows it. | n/a (docs) |
| 4 | Info | Until the one manual `pkill`, a 0.4.x server costs each utterance about three extra local socket round trips under the lock. | Accepted: temporary (ends at the one-time `pkill` the README documents), sub-millisecond on a Unix socket, and caching the refusal would add state for a one-off transition. | n/a |
| 5 | Info | The old server's socket removal could in theory race the new server's bind on the same path. | The server records the socket's inode after binding and on exit removes the path only if it is still that inode (`remove_socket`). | `test_socket_removed_only_while_it_is_ours` |
| 6 | Info | A rogue process running as the same user could loop `/quit` to deny speech. | Accepted: that process can already kill the server or remove the socket; the 0600 socket keeps other users out. | n/a |
| 7 | Info | The `retire-overran` marker was never removed. | A successful retire removes it, so it lives only between an overrun and the next clean handoff. | `test_a_person_waiting_is_told_and_an_old_overrun_marker_is_cleared` |
| 8 | Info | `/synth` (`say --out`) was not refused while quitting and a reply in flight could be cut off when the server exited. | `Speaker.synth_request()` refuses `/synth` with 503 once closed and counts replies in flight; `watch_idle` does not exit while one is being written. | `test_quitting_server_refuses_new_speech_but_still_stops` (now checks `/synth`), `test_synth_request_counts_and_is_refused_once_closed`, `test_a_synth_reply_in_flight_holds_the_exit` |
| 9 | Info | Architecture fit: two-process design kept, client stdlib only, additive changes, no restart loop. | Nothing to do. | n/a |

## Risk register

| ID | Risk | Probability / Impact | After mitigation |
| -- | ---- | -------------------- | ---------------- |
| R1 | Foreground commands hang after an update | Medium / Low | Visible: a terminal line explains the wait (finding 1). |
| R2 | A hung player silences all sessions | Low / Medium | Closed: the server exits after 100 s on its own (finding 2). |
| R3 | A dev copy takes over the installed server | Low / Low | Documented separate data dir (finding 3). |
| R4 | Overhead from a 0.4.x server left running | Medium / Low | Accepted, ends at the one-time `pkill` (finding 4). |
| R5 | Socket race at handoff | Very low / Low | Closed: inode check (finding 5). |
| R6 | Same-user denial of speech | Very low / Low | Accepted, no new capability (finding 6). |

## Verification after the fixes

- `python3 -m unittest discover tests`: 140 tests OK (5 new); the timing-sensitive classes
  (WatchIdleTest, QuitTest, EnsureServerTest) passed five runs in a row.
- `uvx ruff check scripts tests`: 29 findings, the same set as `main`.
- The fixes change code after the reviewed commit; S6 tests the new head on real hardware and S7
  reviews it fresh.
