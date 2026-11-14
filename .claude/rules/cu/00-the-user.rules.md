<!-- source: kits/core/rules/00-the-user.rules.md (generated); filled by /cu:init quick setup 2026-11-14 -->

**Precedence tier**: T5 (COPPER Precedence Constitution).

**WHO** - User identity, organisation configuration, and development environment. Applies to all
interactions with the harness (whichever host runs it).

# Rule 00 - The User and Organisation Profile

**Run `/cu:init` to update user sections interactively, or edit manually.** This repository is
public: keep email addresses, locations and private hostnames out of this file.

---

## Organisation Identity

> **Identity slot.** No identity-kit is installed for this repository. claude-speak is a personal
> open-source project (a fork of `kyleoliveiro/claude-speak`), not organisation work.

---

## Project Overview

| User                | Role                      | Primary Focus                                    |
| ------------------- | ------------------------- | ------------------------------------------------ |
| **Lucas Challamel** | Maintainer of the fork    | Voice and avatar features for Claude Code        |

**Project**: claude-speak (fork), with its sibling repository agent-avatar. **Type**: software
development. **Methodology**: Kanban, continuous flow; one story per branch and PR, one release per
milestone.

---

## User 1: Lucas Challamel

### Professional Identity

**Full Name**: Lucas Challamel **Professional Role**: Maintainer **Organisation**: personal
project **Reporting**: none

### Responsibilities

- Decides scope, priorities and design; approves every merge.
- Keeps the fork close to upstream so upstream merges stay easy.

### Communication Adaptation

- Chat replies are terse (caveman style); anything persisted (code, docs, commits, issues, PRs,
  memory) is plain, complete prose.
- Open decisions are asked as clickable options with a recommendation first.
- He often dictates: names can arrive garbled ("clothes" = Claude, "arena" = Serena). Read for
  intent and confirm when unsure.

---

## Communication and Interaction Standards

**Language Specifications**:

- **Primary Language**: English (repository, docs, issues)
- **Secondary Language**: French
- **Formatting Preference**: Markdown
- **Communication Tone**: direct and factual

**Interaction Guidelines**:

- Answer first, then the reason, then the next step.
- End a change with what was skipped and any risk.
- Give the smallest complete change; name features you chose not to build.

## Technical Environment

**Devices**:

- **Primary OS**: Omarchy (Arch Linux, Hyprland) on a desktop and two laptops
- **Version**: rolling

**Editors and Tools**:

- **Code/Writing Editors**: Claude Code in the terminal, Orca for worktrees and agents
- **Terminal**: [TO BE CONFIGURED]
- **Office Suite**: not used for this project
- **Version Control**: Git + GitHub (`gh`)
- **CRM**: none

**Preferences**:

- **File Format**: Markdown
- **Languages**: Python (stdlib-only client, uv inline-deps server)
- **Memory**: Claude auto-memory, Serena memories, Hindsight bank `proj-claude-speak`, and this
  repository's `memory-bank/`

## AI Preferences

- **Agent name**: Claude Code (no custom name)
- **Default language**: English, unless Lucas writes in French
- **File changes**: allowed without asking; ask before anything destructive or outward-facing
- **Always**: work on a branch with a PR; run the tests before claiming done
- **Never**: push to `main`, force-push, or merge without Lucas's explicit approval; link the
  private agent-avatar repository from public issues; commit `opencode.json` or `.hindsight-bank`

## Instructions for AI Agents

### User Identification

There is one user. Adapt to the profile above.

### Shared Guidelines

1. **Evidence-Based**: back claims with test output, command output or file references.
2. **Language Precision**: follow the language specifications above.
