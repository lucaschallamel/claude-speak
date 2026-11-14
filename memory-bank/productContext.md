# Product context

**Last Updated**: 2026-11-14

**Purpose**: why claude-speak exists and who it serves. See [projectbrief.md](projectbrief.md) for
scope.

## Problem

Long Claude Code turns pull Lucas back to the screen to read every reply. Several sessions run at
once, and it is hard to know which one needs attention.

## User

Lucas: runs several Claude Code sessions on Omarchy, dictates with push-to-talk (`voxtype`), and
wants to listen while looking elsewhere.

## Value

- Hear a one-sentence summary instead of reading the reply.
- Hear questions (`AskUserQuestion`) and mid-turn status lines as they happen.
- Later: tell sessions apart by voice and avatar, and never be talked over.

## Experience goals

- Short, natural and interruptible. Silence beats noise.
- Rich enough voices to create distinct characters and the right tone.

## Alternatives

Upstream claude-speak (no summaries, cues or interjections); cloud TTS (needs a key and network).
