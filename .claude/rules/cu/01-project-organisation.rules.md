<!-- source: kits/core/rules/01-project-organisation.rules.md (generated) -->

**Precedence tier**: T4 (COPPER Precedence Constitution).

**WHERE** - Where things belong: the generic project-organisation principle and the two project-type
profiles it dispatches to. Applies to all projects using this framework.

# Rule 01 - Project Organisation

## Principle

Organise by **actionability and lifecycle stage**: separate authoritative/reference material from
active working documents, and both from archived material. Keep the structure shallow, name things
consistently, and never commit secrets. The concrete folder layout depends on the project type , see
the profile selector below.

## Authority principle (generic)

When information conflicts across locations, precedence follows the material's authority:
**authoritative/reference material outranks active working documents, and both outrank archived
material.** Verify claims against the authoritative tier before relying on working or archived
copies; treat authoritative sources as change-controlled. When sources genuinely conflict, flag the
contradiction to the user and resolve by authority tier , never silently choose one version over
another. (An organisation's concrete instantiation of these tiers , which folders map to which level
, lives in that organisation's project-structure profile, not in this core rule.)

## Security floor (all profiles)

Secrets never enter version control. Every project's `.gitignore` excludes at least:

```gitignore
.env
.env.*
secrets/
credentials/
```

Prohibited-operation handling for secrets and environment files is governed by `[SPO]` (Rule 02) and
Rule 07 Control 4.

## Profile selector

Pick the profile matching the project type and load it on demand (both ship in every install as
framework-authoring resources):

- **Knowledge / documentation / second-brain** work , use the **PARA profile**:
  [`project-profile-para.md`](../skills/framework-authoring/resources/project-profile-para.md)
  (`01-projects/` .. `04-archives/`).
- **Software repository** , use the **Software profile**:
  [`project-profile-software.md`](../skills/framework-authoring/resources/project-profile-software.md)
  (`src/`, `tests/`, `docs/`, `config/`, `scripts/`, `memory-bank/`).

An organisation with a specialised structure (for example a consulting delivery practice with
proposal, tender, client, and project hierarchies) installs its own project-structure profile as a
kit rather than carrying it in this core rule.

## General naming conventions

- ISO date prefixes (`YYYYMMDD`) where chronological sorting helps.
- kebab-case, lowercase; no spaces, accents, or special characters.
- Version suffixes (`-v1`, `-v2`) where a document iterates.

Profile-specific conventions live in each profile.

---

Cross-references between the rules: `skills/framework-authoring/resources/rules-reference.md`.
