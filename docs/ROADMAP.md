# Roadmap

**Last Updated**: 2026-11-16

**Purpose**: the milestones and their stories. **Audience**: Lucas and the agents working on claude-speak. GitHub [milestones](https://github.com/lucaschallamel/claude-speak/milestones) and issues are the tracker; each story's spec is in [roadmap/backlog/](roadmap/backlog/), and its live status is on the [Kanban board](roadmap/KANBAN.md).

**Story IDs** are GitHub issue numbers: `US-002` is issue #2. `SP` marks a spike. New stories start as a GitHub issue; then add its file (same number) and a card.

**Order**: milestones are numbered in build order (renamed on 2026-11-16 after the backlog review: Smarter speech became 3, Characters 4). Within a milestone, stories are listed in build order. Parked and cut stories are at the end.

## 1 Foundation

Shipped as v0.3.3 (2026-11-07).

- [x] [US-001](roadmap/backlog/US-001-unit-test-suite-for-the-client.md) ([#1](https://github.com/lucaschallamel/claude-speak/issues/1)): Unit test suite for the client and server pure functions

## 2 Quiet

Never talk over Lucas. Shipped as v0.4.0 (2026-11-15).

- [x] [US-002](roadmap/backlog/US-002-barge-in.md) ([#2](https://github.com/lucaschallamel/claude-speak/issues/2)): Barge-in: stop speaking when dictation starts
- [x] [US-003](roadmap/backlog/US-003-hush-the-session-s-speech-when.md) ([#3](https://github.com/lucaschallamel/claude-speak/issues/3)): Hush the session's speech when a new prompt is submitted
- [x] [US-004](roadmap/backlog/US-004-instant-replay-and-global-stop-replay.md) ([#4](https://github.com/lucaschallamel/claude-speak/issues/4)): Instant replay and global stop/replay hotkeys
- [x] [US-005](roadmap/backlog/US-005-priority-lanes.md) ([#5](https://github.com/lucaschallamel/claude-speak/issues/5)): Priority lanes: urgent speech preempts chatty speech

## 3 Smarter speech (next: release 0.5.0)

Say what matters, when it matters, and keep the plumbing honest.

- [ ] [US-030](roadmap/backlog/US-030-restart-a-stale-server-after-a.md) ([#30](https://github.com/lucaschallamel/claude-speak/issues/30)): Restart a stale server after a plugin update
- [ ] [US-031](roadmap/backlog/US-031-settings-drift-test.md) ([#31](https://github.com/lucaschallamel/claude-speak/issues/31)): Settings drift test
- [ ] [US-006](roadmap/backlog/US-006-speak-permission-prompts-and-alert-the.md) ([#6](https://github.com/lucaschallamel/claude-speak/issues/6)): Speak permission prompts and alert the avatar
- [ ] [US-009](roadmap/backlog/US-009-verbosity-levels-and-skipping-trivial-replies.md) ([#9](https://github.com/lucaschallamel/claude-speak/issues/9)): Verbosity levels and skipping trivial replies
- [ ] [US-032](roadmap/backlog/US-032-mute-one-session-not-all.md) ([#32](https://github.com/lucaschallamel/claude-speak/issues/32)): Mute one session, not all
- [ ] [US-007](roadmap/backlog/US-007-pronounce-code-identifiers-and-paths-as.md) ([#7](https://github.com/lucaschallamel/claude-speak/issues/7)): Pronounce code identifiers and paths as words
- [ ] [US-033](roadmap/backlog/US-033-session-lifecycle.md) ([#33](https://github.com/lucaschallamel/claude-speak/issues/33)): Session lifecycle: state registry, SessionEnd cleanup, log rotation

Then, in the same milestone:

- [ ] [US-035](roadmap/backlog/US-035-durable-config-dir-that-survives-reinstall.md) ([#35](https://github.com/lucaschallamel/claude-speak/issues/35)): Durable config dir that survives reinstall
- [ ] [US-037](roadmap/backlog/US-037-focus-the-session-that-is-waiting.md) ([#37](https://github.com/lucaschallamel/claude-speak/issues/37)): Focus the session that is waiting
- [ ] [US-012](roadmap/backlog/US-012-do-not-disturb-focus-aware-muting.md) ([#12](https://github.com/lucaschallamel/claude-speak/issues/12)): Do-not-disturb, focus-aware muting and a ''while you were away'' recap

## 4 Characters (after 3)

Tell sessions apart, and give the avatar what it needs. Starts with the avatar contract.

- [ ] [US-034](roadmap/backlog/US-034-avatar-integration-contract.md) ([#34](https://github.com/lucaschallamel/claude-speak/issues/34)): Avatar integration contract: what each player run carries
- [ ] [US-036](roadmap/backlog/US-036-distinct-voice-per-session.md) ([#36](https://github.com/lucaschallamel/claude-speak/issues/36)): Distinct voice per session
- [ ] [US-013](roadmap/backlog/US-013-quick-voice-switcher-that-reaches-all.md) ([#13](https://github.com/lucaschallamel/claude-speak/issues/13)): Quick voice switcher that reaches all 54 Kokoro voices
- [ ] [US-016](roadmap/backlog/US-016-personas.md) ([#16](https://github.com/lucaschallamel/claude-speak/issues/16)): Personas: a voice, tone and avatar per session

## Parked

Revisit when the need shows up in daily use.

- [ ] [US-008](roadmap/backlog/US-008-facts-aware-summaries.md) ([#8](https://github.com/lucaschallamel/claude-speak/issues/8)): Facts-aware summaries: tests, files changed, commits
- [ ] [US-010](roadmap/backlog/US-010-french-and-multilingual-replies-with-a.md) ([#10](https://github.com/lucaschallamel/claude-speak/issues/10)): French and multilingual replies with a matching voice
- [ ] [US-014](roadmap/backlog/US-014-voice-blends.md) ([#14](https://github.com/lucaschallamel/claude-speak/issues/14)): Voice blends: custom voices mixed from Kokoro style vectors

## Cut

Closed as not planned on 2026-11-16 (reasons in each story file and issue).

- [ ] [US-011](roadmap/backlog/US-011-optional-local-summarizer-backend-ollama-or.md) ([#11](https://github.com/lucaschallamel/claude-speak/issues/11)): Optional local summarizer backend (Ollama or heuristic)
- [ ] [SP-015](roadmap/backlog/SP-015-second-tts-engine-for-accents-and.md) ([#15](https://github.com/lucaschallamel/claude-speak/issues/15)): Spike: second TTS engine for accents and languages Kokoro lacks (Australian, richer French)

## Related


- [memory-bank/progress.md](../memory-bank/progress.md): status and history
- [dev-journal/](dev-journal/): session notes
