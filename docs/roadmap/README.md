# Roadmap

**Last Updated**: 2026-11-14

The plan and the delivery record for claude-speak (fork): story specs, the board and the COPPER
pipeline trail. **Audience**: Lucas and the agents working on the fork.

## Contents

GitHub issues and milestones are the tracker and the place for discussion. Each issue has a story
file here with the same number (`US-004` = issue #4, `SP-015` = #15), which holds the spec:
acceptance criteria, technical requirements and settled decisions. The milestone overview is
[../ROADMAP.md](../ROADMAP.md).

## Structure

```
roadmap/
├── KANBAN.md                 # board: TODO, DOING, DONE, CARPARK (one card per story file)
├── backlog/                  # one story file per GitHub issue (US-, SP-)
└── pipeline-audit-trail/     # /cu:pipe records, one per story run
    ├── US-004.yaml           # stage-by-stage state and evidence (S0-S10)
    └── artifacts/            # stage deliverables: <ID>-s1-kickoff.md, <ID>-s2-plan.md, ...
```

Keep issue, story file and card in step: a status change in the story file moves its card.

## Related

- [../dev-journal/](../dev-journal/README.md) - session notes
- [../../memory-bank/](../../memory-bank/progress.md) - current state and history
