<!-- source: kits/core/rules/03-memory-bank.rules.md (generated) -->

**Precedence tier**: T4 (COPPER Precedence Constitution).

**CONTINUITY** - Persistent memory framework for AI agents across session resets. Defines file
structure, hierarchy, workflows, and update protocols.

# Rule 03 - The Memory-Bank

**Critical Principle**: your memory resets completely between sessions, so the Memory Bank is your
only link to prior work and its accuracy decides your effectiveness. **You MUST read ALL memory bank
files at the start of EVERY session** - this is not optional.

**The files** **[ORG]**: the six core files at the root of `memory-bank/`, enumerated BY NAME:
`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`, `activeContext.md`,
`progress.md`. Subdirectories (`archive/` and any others) are NOT part of the mandatory read;
consult them on demand. Structure, per-file contents, live-file token budgets and quality standards
load with `rules/03a-memory-bank.rules.md` when a memory-bank file is read; with no memory bank yet,
read it before creating one.

## Core Workflows

### Plan Mode - Starting a Session

**[CWM]** Read in the order listed, focusing on activeContext.md and progress.md; verify
understanding, then present the approach. **[KBT]** If files are incomplete or contradictory, flag
this explicitly before proceeding.

### Act Mode - During Execution

- **Start of task**: Update activeContext.md with "Currently working on: [task]"
- **Significant discoveries**: Add to systemPatterns.md or techContext.md
- **Completion**: Update progress.md, mark task complete in activeContext.md

**[COM]** Update `activeContext.md` every working session; document WHY, not just WHAT; keep the
bank current (a stale memory bank is worse than none).

## Memory Bank Update Triggers

**[SD]** Update it on a new pattern, after a significant change and when context needs
clarification. On **"update memory bank"** you MUST review ALL six files comprehensively
(`commands/memory-update.md`).
