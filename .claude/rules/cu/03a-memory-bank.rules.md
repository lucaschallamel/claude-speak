---
paths:
- '**/memory-bank/**'
---

<!-- source: kits/core/rules/03a-memory-bank.rules.md (generated) -->

**Precedence tier**: T4 (COPPER Precedence Constitution).

# Rule 03a - Memory-Bank Structure, Budgets and Quality

Refines Rule 03 while a memory-bank file is read or edited: structure, live-file budgets, per-file
contents, update triggers and quality. Scoped by `paths` (ADR-054); its always-on anchor is Rule 03.

## Memory Bank Structure (Root+Archive Pattern)

**[ORG]** Files are stored at: `/memory-bank/`

**[ARC]** Architecture (Scaffold-as-Archive Pattern):

- **Root-level working files**: The 6 core files live at memory-bank root for current project work
- **archive/ subdirectory**: history rolled out of the ROLLING live heads (US-261, US-262) and the
  pattern sections rolled out of `systemPatterns.md` (TD-194). **NOT auto-read** , see the Live-File
  Token Budget section below
- **scaffold-context/ subdirectory**: a TEMPLATE ARTEFACT holding Sprint 0 scaffold-creation
  history. Deleted on project instantiation, so it is **absent from most instances, including this
  one**
- **Why this works**: standard structure at root, size-bounded live heads, history recoverable on
  demand, tool compatibility

**[MOD]** File Hierarchy (each file depends on the ones above it):

- **projectbrief.md** is the foundation, shaping all other files
- **productContext**, **systemPatterns**, and **techContext** provide domain context
- **activeContext.md** synthesises current state from domain contexts
- **progress.md** tracks evolution and completion status

---

## Live-File Token Budget (US-263)

**[CWM]** The six core files are read at EVERY session start, so their size is a fixed tax on every
piece of work. This rule long specified "last 1-2 sessions" for `activeContext.md` but named no
budget, so the files drifted well past it. **Budgets are per file** because growth spans 0 to 675
tokens/day: one number would be meaningless for a static file and absurd for one growing 300/day.

| File                | Class        | Growth   | **Budget** |
| ------------------- | ------------ | -------- | ---------- |
| `projectbrief.md`   | STABLE       | ~0       | 2,000      |
| `productContext.md` | STABLE       | ~0       | 2,000      |
| `activeContext.md`  | ROLLING      | +675/day | **6,000**  |
| `progress.md`       | ROLLING      | +269/day | 20,000     |
| `techContext.md`    | ACCUMULATING | +91/day  | 12,000     |
| `systemPatterns.md` | ACCUMULATING | +308/day | 12,000     |
| **Bank total**      |              |          | **54,000** |

STABLE files change only when scope does , the budget is headroom. ROLLING files keep a live head
and push history to an archive (US-261/262), so the budget enforces the split. ACCUMULATING files
grow with the project. `techContext.md` has **no archive yet** , it is where the next drift comes
from. `systemPatterns.md` has an **index-first archive** (TD-194): every story-tagged
`## <pattern> (<STORY-ID>)` section rolls to the archive and leaves one line in the live
`## Pattern index (archived)`, while the must-include sections listed under Core Files never roll.

**Instance observation (this repository, `cl100k_base`, 2026-09-27 , not a claim about yours).** The
figures above were derived here, where `systemPatterns.md` measured **46,599 tokens against 12,000,
roughly 4x over**, never split. Recorded rather than fixed by raising the number: **a budget set to
current reality would enshrine the drift as the standard**, which is what this rule exists to
prevent. Read the growth rates as provenance for how the budgets were chosen; re-measure your own
bank to set or confirm them. TD-194 (2026-10-10) archive-split that file, 47,616 to 6,807 live
tokens, and retired its ratcheted exemption: no core file is exempt from its budget here.

**Two tiers, both hard** once the gate below exists. (1) The **budget** above , exceeding it FAILS,
and the remedy is to roll history to the archive, never to raise the budget. (2) A generous
**smoke-alarm ceiling** far above it (US-261 set 40,000 for a live head) , exceeding that means the
archive discipline was abandoned. Neither warns, because the enforcing battery has **no warn
state**, so a warning tier would be advice rather than policy. The ceiling is generous on purpose:
appending to a live head is CORRECT, and a tight cap that fails on normal work gets switched off.

**Enforcement is per install, and a budget without one is prose.** This rule states the policy; it
does not ship the gate. Each install adds its own check , token-count each live file, compare it to
its budget, fail the build on breach , and wires it into the battery CI already runs. Count with the
tokeniser your models actually use (`cl100k_base` via tiktoken, etc.); a character count divided by
four is an estimate, and it read 10% low here. Standing the gate up is part of adopting this
section, because until it exists the budgets cannot bite. A file that must exceed its budget for a
known, temporary reason takes a **named, dated, capped exemption that fails if the file grows
further**, never a raised budget: the cap makes the debt visible and the story that clears it
deletes the entry.

**Archive files are read ON DEMAND, never automatically.**
`memory-bank/archive/activeContext-archive.md` (US-261), `memory-bank/archive/progress-archive.md`
(US-262) and `memory-bank/archive/systemPatterns-archive.md` (TD-194) are **EXCLUDED from the
mandatory session-start read**. Consult them for history the live head no longer carries. The
exclusion is **mechanical, not a convention**: the mandatory read covers the six core files at
memory-bank root **enumerated BY NAME**, so a subdirectory is outside it. Were that enumeration ever
made a glob over `memory-bank/**`, every archive would silently re-enter the read and every split's
saving would vanish with nothing else failing.

**[COM] The always-read core is unchanged.** All six core files are still read every session. The
budget constrains their SIZE; it makes none of them optional. That guarantee is what keeps a session
recoverable on any host and model.

---

## Core Files (Required)

### 1. projectbrief.md - Foundation Document

**[SD]** Purpose: Source of truth for project scope, requirements, and goals

**Must Include**:

- **Project Name & Identifier**: Full name, project instance ID (e.g., PC123456)
- **Core Objectives**: Primary goals and success criteria
- **Scope Definition**: What's in scope, what's explicitly out of scope
- **Stakeholders**: Who cares about this project and why
- **Constraints**: Technical, business, timeline, budget limitations
- **Success Metrics**: How we measure project success

**[COM]** Created at project start if it doesn't exist. Updated rarely (only for scope changes).

### 2. productContext.md - The "Why"

**[SD]** Purpose: Explains why this project exists and the problems it solves

**Must Include**:

- **Problem Statement**: What user/business pain are we addressing?
- **User Personas**: Who will use this? Their needs, goals, frustrations
- **Value Proposition**: How does this solution help? What makes it valuable?
- **User Experience Goals**: How should users feel when using this?
- **Competitive Context**: Alternatives, our differentiation
- **Success Stories**: What does success look like for users?

**[RP]** Written for humans and AI agents - clear, narrative style

### 3. activeContext.md - Current Work Focus

**[CWM]** Purpose: Most frequently updated file - tracks current session context

**Must Include**:

- **Current Sprint/Phase**: What phase of development are we in?
- **Active Work Items**: What's being worked on right now?
- **Recent Changes**: Significant changes in last 1-2 sessions (with dates)
- **Next Steps**: Immediate priorities and upcoming work
- **Active Decisions**: Pending decisions, ADRs in progress
- **Important Patterns**: Coding patterns, architectural decisions being applied
- **Session Learnings**: Insights discovered during recent work
- **Blockers**: Current impediments and their workarounds

**[TR]** Document WHY decisions are made, not just WHAT was done

**Update Frequency**: Every session where significant work occurs

### 4. systemPatterns.md - Architecture & Design

**[ARC]** Purpose: Captures system architecture and design patterns

**Must Include**:

- **System Architecture**: High-level structure (microservices, layers, components)
- **Key Technical Decisions**: Major architectural choices and their rationale
- **Design Patterns in Use**: Patterns actively used (with locations/examples)
- **Component Relationships**: How major components interact
- **Critical Implementation Paths**: Important workflows and their implementations
- **Anti-Patterns to Avoid**: Known bad practices for this project
- **Architectural ADRs**: Links to detailed Architecture Decision Records

**[MOD]** Separate concerns - architecture here, technologies in techContext.md

**Where a new pattern goes** (TD-194): write it as a `## ` heading that ENDS in a parenthetical
carrying its story id, `## <pattern> (<STORY-ID>[, ...])`, where the id is `US-`, `TD-`, `BUG-`,
`SEC-`, `SP-`, `EP-` or `CI-` plus digits; a tag elsewhere in the heading does not make it a
pattern. At the next `/cu:memory-update`, `prune-memory-bank.py` rolls it, with any tagged `### `
children, to `archive/systemPatterns-archive.md` and leaves one line per pattern in
`## Pattern index (archived)`. Only the TITLE stays live, so a lesson every session must apply
belongs in a must-include section (for example Anti-Patterns to Avoid), which is matched by exact
heading and never rolls.

### 5. techContext.md - Technologies & Setup

**[ENV]** Purpose: Documents technical environment and development setup

**Must Include**:

- **Technology Stack**: Languages, frameworks, libraries (with versions)
- **Development Environment**: OS, IDE, tools, containerisation (Podman/Docker)
- **Infrastructure**: Cloud providers, databases, message queues, caches
- **Development Setup**: How to get a local environment running
- **Technical Constraints**: Performance requirements, compliance needs, platform limitations
- **Dependencies**: Critical dependencies and version pinning rationale
- **Tool Usage Patterns**: How we use specific tools (testing frameworkes, linters, etc.)

**Update Trigger**: When tech stack changes (new library, version upgrade, tool addition)

### 6. progress.md - Status & Evolution

**[TST]** Purpose: Track what works, what's left, and project evolution

**Must Include**:

- **Completed Features**: What's done and working (with dates)
- **In Progress**: Current work items and their status
- **Remaining Work**: Backlog, upcoming features, technical debt
- **Known Issues**: Bugs, technical debt, areas needing improvement
- **Metrics**: Test coverage, performance benchmarks, quality metrics
- **Decision Evolution**: How and why decisions changed over time
- **Lessons Learned**: What we'd do differently, what worked well

**[RAT]** Note which rules/principles guided completed work

**Format**: Chronological or status-based organisation (choose what fits project)

---

## Additional Context Files/Folders

**[ORG]** Create additional files within `memory-bank/` when they help organise complex information.

### Complete Structure (Root+Archive)

```
memory-bank/
├── projectbrief.md           # Required (root - current project)
├── productContext.md         # Required (root - current project)
├── activeContext.md          # Required (root - current project)
├── systemPatterns.md         # Required (root - current project)
├── techContext.md            # Required (root - current project)
├── progress.md               # Required (root - current project)
│
├── archive/                  # NOT auto-read: history rolled out of the live heads
│   ├── activeContext-archive.md  # Story-session history (US-261)
│   ├── progress-archive.md       # Milestone history (US-262)
│   └── systemPatterns-archive.md # Rolled pattern sections (TD-194)
│
├── handover.md               # Optional: session handover notes
│
├── scaffold-context/         # TEMPLATE ARTEFACT: Sprint 0 history from scaffold
│                             # creation. Deleted on project instantiation, so it is
│                             # ABSENT from most instances (including this one).
│                             # Shown for template lineage, not expected on disk.
│
├── features/                 # Optional: Complex feature docs
│   ├── feature-name-1.md
│   └── feature-name-2.md
│
├── integrations/             # Optional: Integration specs
│   ├── third-party-api.md
│   └── internal-service.md
│
├── architecture/             # Optional: architecture, ADRs, APIs, technical designs
│   └── endpoint-catalog.md
│
├── testing/                  # Optional: Testing strategies
│   ├── test-strategy.md
│   └── test-data-management.md
│
└── deployment/               # Optional: Deployment procedures
    └── deployment-runbook.md
```

**[DRY]** Don't duplicate. If info exists in `/architecture/apis/`, link to it rather than copying.

---

## Update Triggers and Actions

The command trigger ("update memory bank") is in Rule 03 and `/cu:memory-update`.

### 1. Discovering New Project Patterns

**Examples**:

- Found a better way to organise code
- Identified a useful architectural pattern
- Discovered a tool configuration that works well

**Action**: Update **systemPatterns.md** or **techContext.md** with the pattern and rationale

### 2. After Implementing Significant Changes

**Examples**:

- Completed a major feature
- Refactored significant code
- Changed architectural approach
- Upgraded dependencies

**Action**: Update **progress.md** (what's done), **activeContext.md** (remove from active work),
**systemPatterns.md** or **techContext.md** (if architecture/tech changed)

### 4. When Context Needs Clarification

**Examples**:

- Starting work and unsure of current state
- Memory bank files seem contradictory
- Missing critical information
- About to make a major decision

**Action**: Pause, review relevant memory bank files, ask user to clarify, then update memory bank
with clarification

---

## Quality Standards for Memory Bank

### File Quality Requirements

**[RP] Readability Priority**:

- ✅ Clear, concise language
- ✅ Structured with headings and bullet points
- ✅ Examples where helpful
- ✅ Dates on time-sensitive information
- ❌ No jargon without explanation
- ❌ No outdated information

**[SD] Strategic Documentation**:

- ✅ Focus on WHY, not just WHAT
- ✅ Context around decisions
- ✅ Links to detailed docs when appropriate
- ❌ No unnecessary duplication
- ❌ No obvious or trivial statements

**[TST] Test Coverage for Memory Bank**:

- Can a new AI agent understand the project from these files alone?
- Are there contradictions between files?
- Is the current state clearly described?
- Are next steps actionable?
