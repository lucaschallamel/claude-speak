---
paths:
- '**/{roadmap,backlog,dashboards}/**'
---

<!-- source: kits/core/rules/04c-backlog.rules.md (generated) -->

**Precedence tier**: T4 (COPPER Precedence Constitution).

# Rule 04c - Task and Backlog Management

Loaded while a backlog, roadmap or board file is touched: the Kanban structure and its
synchronisation rule. Scoped by `paths` (ADR-054); its always-on anchor is Rule 04.

## Task & Backlog Management Standards

**Kanban Board Structure**: All project backlogs use a 4-column Kanban structure:

| Column      | TODO Status Values                            | Purpose                        |
| ----------- | --------------------------------------------- | ------------------------------ |
| **TODO**    | `todo`, `pending`, `scheduled`                | Backlog, not started           |
| **DOING**   | `in-progress`, `active`, `delegated`          | Work in progress               |
| **DONE**    | `completed`, `done`                           | Successfully finished          |
| **CARPARK** | `blocked`, `cancelled`, `deferred`, `on-hold` | Blocked, deferred or cancelled |

**Synchronisation Rule**: When updating a TODO note's `status:` field, the corresponding Kanban card
MUST move to the matching column. See `@skills/kanban-board-management/SKILL.md` for complete
guidance.

**Primary Owner**: the agile-coaching / delivery-lead role manages Kanban boards and backlog
synchronisation (whichever agent an installed kit provides for that role).
