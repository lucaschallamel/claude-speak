# US-004 S1 Kickoff: Instant replay and global stop/replay hotkeys

**Date**: 2026-11-14 | **Profile**: standard | **Story**:
[US-004](../../backlog/US-004-instant-replay-and-global-stop-replay.md) (issue #4)

**Purpose**: S1 review of US-004 (scope, ACs, feasibility, risks) and the plan it feeds into S2.
**Audience**: Lucas and the agent running the pipeline.

## Findings from the code

- There is no "last WAV" to keep. `Speaker._run` (`scripts/server.py:281`) synthesises each sentence
  chunk into its own temp WAV and deletes it after playing. Replay has to keep the chunks' samples
  in memory, without the lead-in silence (it is added fresh at play time, `lead_in()`).
- Playback goes through the player command for each chunk (`_spawn`, `server.py:230`). With
  `CLAUDE_SPEAK_PLAYER=avatar-play`, a replay passes through the same player, so the avatar's mouth
  moves. The `[mood gesture]` cue is sent by the client, not the server, so a replay does not resend
  it. This is acceptable for this story.
- `claude-speak stop` already exists (`cmd_stop`, `scripts/claude_speak.py:836`) and does not start
  the server. `again` should behave the same way: if the server is not running, there is nothing to
  replay, so it does not start one.
- **Hotkeys have no plugin data dir.** Outside Claude Code, `data_dir()` (`claude_speak.py:124`)
  falls back to `~/.local/share/claude-speak`. That is a different socket from the installed
  plugin's `~/.claude/plugins/data/claude-speak-claude-speak/`, so a plain hotkey would silently do
  nothing. The installed `bin/` path also contains the version (`cache/.../0.3.3/bin`) and changes on
  every update.

## Decisions (Lucas, 2026-11-14)

1. **Replay interrupts, queue kept**: replay stops the clip playing now and plays at once; queued
   speech plays after it. The interrupted clip is lost, as with a new prompt.
2. **Hotkey path: README wrapper script**: a small `~/.local/bin/claude-speak` picks the newest
   installed version and sets `CLAUDE_SPEAK_DATA` to the plugin data dir. No change to
   `data_dir()`.

## Challenge Log

**Story**: US-004 | **Profile**: standard | **Entries**: 6

| #   | Aspect               | Challenge                                                                                                                                       | Disposition                                                                                                                                                                                           | Status   |
| --- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 1   | Scope stress-test    | Does "replay" overlap with `/rephrase` or #5 priority lanes?                                                                                    | No overlap. Replay replays the audio already made, with no new summary or synthesis; `/rephrase` stays the slow "say it differently". Replay interrupts directly; general preemption stays in #5.      | resolved |
| 2   | AC testability       | "Replay starts in under 300 ms" depends on the audio device and player, which CI cannot measure.                                                | Unit-test the part we control: replay queues the stored chunks with no call to `synth` (asserted with a stub). The 300 ms target is checked by hand on omarchy and recorded in S6.                     | resolved |
| 3   | Risk surfacing       | A hotkey run outside Claude Code talks to the wrong socket (`~/.local/share/claude-speak`), and the versioned `bin/` path breaks on every update. | Decision 2: README wrapper that resolves the newest installed version and sets `CLAUDE_SPEAK_DATA`. Added as an AC.                                                                                   | resolved |
| 4   | Risk surfacing       | What is "the last clip" when speech was interrupted (barge-in, hush, a newer reply) before synthesis finished?                                  | Store a clip only once all its chunks are synthesised. An interrupted, half-made utterance is never stored; replay then plays the previous complete one. Replays are never stored themselves.            | resolved |
| 5   | Risk surfacing       | Memory: samples kept per session could grow with many sessions.                                                                                 | 24 kHz float32 is about 96 KB/s, so a 20 s summary is about 2 MB. Keep one clip per session and drop sessions not heard from in an hour (the same idea as `last_seen`). In memory only; gone on restart. | resolved |
| 6   | Dependency freshness | Does the story still match main after #2 barge-in and #3 hush changed `stop`?                                                                   | Yes. Replay reuses `_cancel_current` and the queue; barge-in and hush stop a replay like any other speech. No other story is needed first.                                                            | resolved |

## Review criteria

- **Scope**: bounded; one server endpoint, one client subcommand, README. Fits a 2-point story.
- **Requirements**: ACs sharpened below; edge cases (no server, nothing stored, interrupted clip)
  now explicit.
- **Feasibility**: reuses `Speaker`, `Job` and the player path; no new dependency; the client
  stays stdlib-only.
- **DoD**: unit tests for the server and the client, README section, CI green on Linux and macOS.

## Implementation plan (input to S2)

1. **Server**: on a non-replay job whose chunks are all synthesised, store `(samples list, rate)`
   per session plus the most recent session id. `POST /replay {session?}` builds a replay job from
   the stored chunks (fresh lead-in), interrupts the current clip, puts the job at the front of the
   queue; `404` when nothing is stored.
2. **Client**: `claude-speak again [--session]`: if the server is not running or replies 404, print
   `claude-speak: nothing to replay.`; never starts the server.
3. **Tests**: replay without synthesis, front-of-queue plus interrupt, interrupted clip not stored,
   404 when empty, client prints without starting the server.
4. **Docs**: README "Hotkeys" section with the wrapper script and Hyprland binds for stop and
   replay, including `claude-speak stop; voxtype record start` as a barge-in for setups with no
   state file. CLAUDE.md endpoint list gets `/replay`.

**Estimated effort**: about half a day.

## Risk register

| ID  | Risk                                                        | Probability | Impact | Mitigation                                                     |
| --- | ----------------------------------------------------------- | ----------- | ------ | -------------------------------------------------------------- |
| R1  | Hotkey talks to the wrong server                            | High        | Medium | README wrapper sets `CLAUDE_SPEAK_DATA` (decision 2)           |
| R2  | Replay plays a half-made utterance                          | Medium      | Low    | Store only fully synthesised clips (challenge 4)               |
| R3  | 300 ms target missed because of player start-up             | Low         | Low    | Measured by hand at S6; chunks are ready, no synthesis on path |
