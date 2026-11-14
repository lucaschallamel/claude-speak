---
paths:
- '**/*.md'
---

<!-- source: kits/core/rules/02c-task-notation.rules.md (generated) -->

**Precedence tier**: T3 (COPPER Precedence Constitution).

# Rule 02c - Task Genius Notation

The notation that Rule 02's Task Genius obligation requires, loaded when a Markdown file is touched.
Scoped by `paths` (ADR-054); its always-on anchor is Rule 02.

## Task Genius Notation Standard

**Status Characters** (8 Symbols):

| Syntax  | Status          | Use Case                       |
| ------- | --------------- | ------------------------------ |
| `- [ ]` | **Todo**        | New tasks, backlog items       |
| `- [x]` | **Completed**   | Finished work                  |
| `- [/]` | **In Progress** | Active work                    |
| `- [-]` | **Cancelled**   | Obsolete, changed requirements |
| `- [>]` | **Delegated**   | Assigned to someone else       |
| `- [<]` | **Scheduled**   | Planned for specific date      |
| `- [?]` | **Question**    | Blocked, needs clarification   |
| `- [!]` | **Important**   | Urgent, high priority          |

## Mandatory GTD Compliance

All Agents MUST:

1. ✅ Use Task Genius notation for ALL actionable items
2. ✅ Be specific in task descriptions
3. ✅ Assign ownership when delegating (**[>]**)
4. ✅ Include deadlines for scheduled tasks (**[<]**)
5. ✅ Prioritise urgent tasks (**[!]**)
6. ✅ Track progress with status updates
7. ✅ Flag questions requiring clarification (**[?]**)
8. ✅ Cancel obsolete tasks explicitly (**[-]**)

**Full Documentation**: See `skills/gtd-notation/SKILL.md` for complete formatting guidelines,
agent-specific examples, task lifecycle management, and Obsidian integration details.

---

## Formatting and example

Be specific (action verbs + deliverables); assign ownership with `[>]`; include deadlines with
`[<]`; prioritise urgent tasks with `[!]`; track progress via status updates. A worked multi-phase
example is on-demand at `skills/gtd-notation/resources/task-management-example.md`.
