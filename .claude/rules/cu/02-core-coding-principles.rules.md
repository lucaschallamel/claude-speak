<!-- source: kits/core/rules/02-core-coding-principles.rules.md (generated) -->

**Precedence tier**: T3 (COPPER Precedence Constitution).

**HOW** - Implementation principles, security requirements, and code-level standards governing all
development work.

# Rule 02 - Core Coding Principles

Scoped refinements: `rules/02a-code.rules.md`, `rules/02b-dependencies.rules.md`,
`rules/02c-task-notation.rules.md`.

## Core Implementation Principles

- **[SF] Simplicity First**: prioritise the simplest viable solution; complex patterns need explicit
  justification.
- **[RP] Readability Priority**: code must be immediately comprehensible to humans and AI systems.
- **[DM] Dependency Minimalism**: add a library or framework only on explicit request or compelling
  technical justification.
- **[ISA] Industry Standards Adherence**: follow the language's and framework's conventions.
- **[SD] Strategic Documentation**: document complex logic and critical functions; skip the obvious.
- **[TDT] Test-Driven Thinking**: design all code for testability from the first implementation.

**Principle Tagging (advisory)**: Code decisions SHOULD be tagged with principle codes (e.g.
**[SF]**) where it aids traceability; a tag is not a substitute for applying the principle.

---

## Quality Assurance Standards

### Mandatory Quality Guarantees

**[DRY] Don't Repeat Yourself**: Eliminate all code duplication through reuse and extension of
existing functionality.

**[CA] Clean Architecture**: Maintain consistently formatted, logically structured code following
established patterns.

**[REH] Robust Error Handling**: Implement comprehensive error handling for all edge cases and
external system interactions.

Code-smell thresholds, quality metrics and coverage targets: `rules/02a-code.rules.md`.

## Workflow & Change Management

### Workflow Principles

**[FOC] Focus on Relevant Code**: Focus on areas of code relevant to the task.

**[SCP] Scope Protection**: Do not touch code unrelated to the task.

**[TST] Test Coverage**: Write thorough tests for all major functionality.

**[ARC] Architecture Stability**: Avoid major changes to working patterns/architecture unless
explicitly requested.

**[IMP] Impact Analysis**: Consider what other methods and areas might be affected by changes.

### Change Standards

**[AC] Atomic Changes**: Make small, self-contained modifications for traceability and rollback.

**Rules** **[SCP]**:

- Make only requested changes or those confidently understood and related to the request
- When fixing bugs, exhaust existing implementation options before introducing new patterns
- Remove old implementation when introducing new patterns to avoid duplicate logic

### Commit Standards

**[CD] Commit Discipline**: Regular commits in
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format,
`type(scope): concise description`, with an optional body and a footer for breaking changes and
issue references. **Types**: feat, fix, docs, style, refactor, perf, test, chore.

---

## Mandatory Security Standards

### Core Security Principles

**[IV] Input Validation**: All external data must undergo comprehensive validation before any
processing.

**[SFT] Security-First Thinking**: Implement robust authentication, authorisation, and data
protection as foundational requirements.

**[RM] Resource Management**: Properly close all connections and free system resources to prevent
leaks.

**[CMV] Constants Over Magic Values**: Eliminate magic strings and numbers; use descriptive named
constants exclusively.

### Non-Negotiable Security Controls

- **[RL] Rate Limiting**: Implement rate limiting on ALL API endpoints without exception.
- **[RLS] Row Level Security**: Apply row-level security consistently across all data access.
- **[CAP] CAPTCHA Integration**: Mandatory CAPTCHA on all authentication routes and signup pages.
- **[WAF] Web Application Firewall**: Enable attack challenge mechanisms on the WAF.

### Absolute Security Restrictions

> [!warning] PRIOR APPROVAL REQUIRED , do not proceed without it
>
> **[SPO] Secure Prohibited Operations** are hard-gated, not advisory:

- Reading or modifying .env files or environment configuration
- Accessing `_/config/secrets.*` or any secrets management files
- Handling any files containing API keys, credentials, or sensitive authentication data

**Governance**: These operations require explicit user approval before execution.

**Configuration Protection**: Never overwrite .env files without explicit user confirmation; back up
a configuration file before modifying it; document every configuration change with its rationale.

Before adding or upgrading a dependency, by manifest edit or package-manager command, apply
`rules/02b-dependencies.rules.md` (**[PKV]** verified packages, **[DCH]** documented changes).
Before creating a source file, read `rules/02a-code.rules.md` (size limits, script placement, no
fake data outside tests).

---

## AI Communication & Transparency

### Enhanced Communication Framework

- **[RAT] Rule Application Tracking**: advisory tagging of rule applications for traceability (an
  annotation that aids audit, not a mandatory gate).
- **[TR] Transparent Reasoning**: state which rules and principles shaped a decision.
- **[EDC] Explanation Depth Control**: scale detail to the complexity and the context.
- **[AS] Alternative Suggestions**: offer alternative approaches with their pros and cons.
- **[KBT] Knowledge Boundary Transparency**: say clearly when a request exceeds your capabilities or
  available context.
- **[CWM] Context Window Management**: manage context limits proactively; recommend a session
  transition when needed.

---

## Task Management & GTD Integration

**Principle**: ALL markdown outputs containing actionable items MUST use Task Genius notation for
seamless integration with the user's Obsidian-based GTD (Getting Things Done) workflow.

Read `rules/02c-task-notation.rules.md` (the eight status characters) before writing them; full
guide: the `cu:gtd-notation` skill.

---

Quality gates (pre-commit, CI, peer review): `rules/02a-code.rules.md`; this framework's own:
`commands/quality-review.md`, `commands/qa-gate.md`. Rule dependency map:
`skills/framework-authoring/resources/rules-reference.md`.
