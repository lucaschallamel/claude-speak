---
paths:
- '{kits,.claude,.opencode}/**'
---

<!-- source: kits/core/rules/04b-framework-versioning.rules.md (generated) -->

**Precedence tier**: T3 (COPPER Precedence Constitution).

# Rule 04b - Framework File Versioning

Loaded while a framework file (kit source or deployed harness tree) is touched: per-file semver and
change history. Scoped by `paths` (ADR-054); its always-on anchor is Rule 04.

## Maintaining `instructions.md`

### When to Update `instructions.md`

- **New principle codes** - Add to registry with clear description
- **New rules** - Add to cross-reference map and quick reference index
- **Framework changes** - Update hierarchy or core behaviours
- **Values evolution** - Update organisation alignment in Rule 00

### Version Control

- `instructions.md` follows semantic versioning (MAJOR.MINOR.PATCH)
- All changes require peer review and stakeholder approval
- Changes propagate to dependent rules automatically via references

## Per-File Frontmatter Versioning (MANDATORY)

**[CD] [ORG]** Semantic versioning governance for all framework files with YAML frontmatter.

**Applies to**: ALL framework files with a `version` field in YAML frontmatter, including but not
limited to:

- `instructions.md`
- `AGENTS.md`
- `README.md`
- `rules/*.md` (all rule files including `06-principles-registry.rules.md`)
- `skills/*/SKILL.md` (all skill files)
- `commands/*.md` (all command files)
- `tools/*` (custom tool files, where applicable)

**Decision test**: "Does this change **add** a new capability, or does it **fix/update** something
existing?" If the latter, it is a PATCH.

| Bump  | When to Use                                                                                         | Examples                                                      |
| ----- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| PATCH | Fixes, corrections, reference updates, count updates, description tweaks, documentation corrections | Updated skill count, fixed cross-reference, clarified wording |
| MINOR | New capabilities, new sections, backward-compatible structural additions                            | Added new skill, new command, new pipeline stage              |
| MAJOR | Breaking changes to the file's contract or interface                                                | Removed a section, changed required frontmatter fields        |

**Change history is externalised (US-339)**: per-file frontmatter carries only `version` +
`last_updated`, never an inline `changelog:` block. That block loaded into every agent's context on
every session for zero runtime value. Record the "why" of each change in the **per-kit**
`CHANGELOG.md` at the kit root (never inside a glob-loaded asset folder; see `kits/SPEC.md` s.3.1),
and it is preserved in git history. History does NOT belong in a body-level `## Changelog` section
of an asset file either , the CHANGELOG.md is its one home. The `markdown-governance` gate rejects a
re-introduced inline `changelog:` key.

**Enforcement**:

- Every `version` bump MUST use the correct level (the decision test above); record the change in
  the kit-root `CHANGELOG.md`, not in the file's frontmatter or a body section.
- The framework release tag (README badges, root `CHANGELOG.md` release sections) is a **separate
  concern** that rolls up file-level changes into a single release version.
- When in doubt, default to PATCH.
