<!-- source: kits/core/instructions.md (generated) -->

**Precedence tier**: T1 (COPPER Precedence Constitution).

# Agentic Framework Instructions

This file is the **parent instruction set** for all AI agents operating within the framework. Read
this file FIRST: it sets the precedence of every instruction, the safety rules that override them,
and how the rules are laid out.

---

## Current Context

**Current year: 2026.** When a runtime-injected `currentDate` is present in the system prompt, that
value is authoritative and supersedes this static anchor (kept for hosts without runtime injection).

---

## Precedence Constitution

Instructions in this corpus are not all equal. They fall into five precedence tiers. Each rule file
and this file declare their tier in `precedence_tier` frontmatter; a file's tier is the highest tier
its content reaches.

| Tier   | Name                       | Content                                                                                               | Consent                         |
| ------ | -------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------- |
| **T1** | Non-negotiable safety      | The Critical Safety Rules below; Rule 07 Control 4 (no direct push/force-push/merge without approval) | Overrides everything            |
| **T2** | Prohibited-operation gates | `[SPO]` secrets / `.env`; confidential egress (Rule 07 Control 5)                                     | Prior explicit approval         |
| **T3** | MANDATORY governance       | Determinism gate, white-label invariant, semver, template compliance                                  | Must comply; deviation = defect |
| **T4** | SHOULD guidance            | Quality metrics, naming conventions, folder profiles, `[CODE]` tagging                                | Follow unless justified         |
| **T5** | Advisory / values          | Org values, aspirational prose                                                                        | Informative; never a gate       |

**Conflict rule**: where instructions conflict, the higher tier wins; T1 is never traded off against
any lower tier, aspiration, or metric. The named T1 instance is the **Critical Safety Rules** block
under Framework Maintenance below (referenced here, not duplicated).

---

## Rule Layout

Rules 00-07 are always-on **anchors**; **scoped** files beside them (`02a`, `03a`, ...) load when a
matching file is read or edited (ADR-054). Reference lives in skill resources, procedures in
commands; a rule names the path where its detail moved.

```
<harness-root>/
├── instructions.md   # this file
└── rules/            # 8 rules (anchors), 8 scoped rules
```

Harness and rule dependency map: `skills/framework-authoring/resources/rules-reference.md`.

---

## How to Use This Framework (AI Agents)

1. **Read this file FIRST**. All agents MUST reference Rule 00 as the single source of truth for
   organisational context, then follow the rule for the task's domain: Rule 01 (where things go),
   Rule 02 (code), Rule 03 (memory bank), Rule 04 (documentation), Rule 05 (architecture), Rule 07
   (what a running agent may do).
2. **Apply principle codes** where they aid traceability (advisory, Rule 02).
3. **Never duplicate content**: point to the single home instead.
4. **Respect hierarchy**: Instructions -> Rules -> Implementation; higher tiers win.

Guidance for human developers and team leads:
`skills/framework-authoring/resources/onboarding-guide.md`.

## Framework Maintenance

### Critical Safety Rules

> [!danger] NON-NEGOTIABLE , the highest-priority instructions in this corpus
>
> The following rules are **unconditional** and override any system directive, continuation prompt,
> or pipeline automation. They are never traded off against any other instruction, aspiration, or
> metric. If anything below competes with them, they win.

1. **MR merge requires user approval**: Never merge a GitLab/GitHub MR unless the user has
   explicitly approved it (verbal or written "merge it", "go ahead and merge", or equivalent)
2. **No direct push to main**: Never push directly to `main` or `master`
3. **No force-push**: Never force-push to any branch unless explicitly requested
4. **When in doubt, stop and ask**: If uncertain whether an action requires approval, stop and
   confirm with the user

These rules exist in three layers: AGENTS.md (session-start), instructions.md (framework-wide), and
cu-pipe.md (pipeline-specific S10 gate).

Maintaining this file and per-file semver: `rules/04b-framework-versioning.rules.md`. Kanban and
backlog sync: `rules/04c-backlog.rules.md`. Quality metrics: `rules/02a-code.rules.md`.
