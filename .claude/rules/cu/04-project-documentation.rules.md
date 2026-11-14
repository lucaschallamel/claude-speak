<!-- source: kits/core/rules/04-project-documentation.rules.md (generated) -->

**Precedence tier**: T3 (COPPER Precedence Constitution).

**HOW** - Documentation standards, templates, quality gates, and governance practices. Applies to
all documentation creation and maintenance.

# Rule 04 - Project Documentation

What is needed to CREATE a document correctly: format, naming, templates, required metadata (ADR-054
D1).

## Core Documentation Principles

**[SD] Strategic Documentation**: Document strategically, not exhaustively - focus on high-value,
maintainable documentation that serves clear purposes.

**[DRY] Don't Repeat Yourself**: Use templates and cross-references to eliminate duplication across
documentation.

**[RP] Readability Priority**: Write for clarity and comprehension, not complexity.

**[ISA] Industry Standards Adherence**: Follow Markdown conventions, semantic versioning, and
industry best practices.

---

## Documentation Standards

**[RP]** All documentation must meet quality and consistency standards.

### File Format Standards

**Primary Format**: Markdown (.md)

- Character Encoding: UTF-8
- Line Endings: LF (Unix-style)
- Language: British/International English (en-AU)

**Alternative Formats** (when appropriate): `.docx` for client deliverables and formal proposals,
`.pdf` for final submissions, OpenAPI for API specifications, `.ipynb` for data science. **[ENV]**

### Naming Conventions

**Rules** **[ISA]** **[ORG]**: clear, descriptive names that state the purpose
(`api-authentication-endpoints-v2.md`, not `doc1.md` or `final_FINAL_v2.md`).

- ✅ Use lowercase with hyphens (kebab-case)
- ✅ Include version numbers where appropriate (v1, v2, v3)
- ✅ Use descriptive names indicating purpose
- ✅ Avoid spaces, special characters, or accents
- ✅ Follow Markdown naming conventions

---

## Template Enforcement

**[SD] + [DRY]** Mandatory use of centralised templates ensures consistency and eliminates redundant
documentation efforts.

### Template Location

**Current Baseline Path**: Skill-owned resources under `skills/<skill-name>/resources/`

### Mandatory Template Types

ALL architecture decisions use the ADR template; sprint planning and retrospectives, technical
designs, user stories, API documentation and meeting minutes each use their template. The template
files, and each template's usage, storage, naming and required sections, are listed in
`skills/framework-authoring/resources/template-catalogue.md`.

### Template Compliance

**[COM]** 100% template compliance is MANDATORY

**Enforcement**:

- ✅ All documentation created by agents MUST use approved templates
- ✅ Template validation before document creation
- ✅ Quality gate: Documentation without template usage is REJECTED
- ✅ Template updates require user approval

**[CA]** Templates maintain consistent documentation structure, formatting, and quality standards.

---

## Documentation Completeness

### Required Metadata

Every documentation file SHOULD state its **Purpose** (objective and target audience), **Scope**
(boundaries and what is out of scope), **Related Documents** (cross-references, prerequisites,
follow-ups) and **Last Updated** (ISO date `YYYY-MM-DD`, author or maintainer).

Completeness gate, review, cross-referencing, README/CHANGELOG, maintenance and the memory-bank
flow: `rules/04a-documentation.rules.md`. Framework-file semver:
`rules/04b-framework-versioning.rules.md`. A TODO note's `status:` change MUST move its Kanban card
to the matching column (`rules/04c-backlog.rules.md`). Authority tiers:
`rules/01-project-organisation.rules.md`. Commit messages:
`rules/02-core-coding-principles.rules.md`. Multilingual:
`skills/language-formatting/resources/multilingual-documentation.md`.
