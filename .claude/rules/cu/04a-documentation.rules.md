---
paths:
- '**/*.md'
---

<!-- source: kits/core/rules/04a-documentation.rules.md (generated) -->

**Precedence tier**: T3 (COPPER Precedence Constitution).

# Rule 04a - Documentation Completeness, Review and Maintenance

Refines Rule 04 while a Markdown file is touched: completeness gate, review, quality gates,
cross-referencing, README and CHANGELOG files, maintenance. Scoped by `paths` (ADR-054); its
always-on anchor is Rule 04.

## Documentation Completeness

**[SD]** Documentation must include mandatory sections for discoverability and maintenance.

### Completeness Quality Gate

**Incomplete documentation is REJECTED** if missing:

- [ ] Clear purpose statement
- [ ] Defined scope and boundaries
- [ ] Target audience identification
- [ ] Last updated timestamp
- [ ] Required template sections (if applicable)
- [ ] Cross-references to related documents

---

### Documentation Review Process

**Review Requirements** **[COL]**:

- Architecture documentation → Architect approval
- API documentation → API designer review
- Customer-facing documentation → Product team approval
- ADRs → Peer review and stakeholder sign-off
- Sprint documentation → Scrum Master validation

**Review Checklist**:

- [ ] Template compliance verified
- [ ] Completeness requirements met
- [ ] Technical accuracy validated
- [ ] Cross-references integrity checked
- [ ] Language and tone appropriate
- [ ] No confidential information exposed

---

## Quality Gates & Enforcement

**[COM]** Documentation governance is enforced through automated and manual quality gates.

### Automated Enforcement

**Pre-Commit Checks**:

- Documentation location validation (per Rule 01)
- Template compliance verification
- Naming convention validation
- Markdown linting (formatting, broken links)
- Character encoding validation (UTF-8)
- Line ending consistency (LF)

**CI/CD Integration**:

- Documentation completeness checks
- Cross-reference integrity validation
- Orphaned document detection
- Template version validation
- Broken link detection
- Spelling and grammar checks

### Severity Levels

**Critical** (BLOCK merge/deployment):

- Template non-compliance
- Missing required sections
- Broken critical cross-references
- Security information exposure

**High** (Require fixes before merge):

- Incomplete metadata
- Naming convention violations
- Significant formatting issues
- Unclear purpose or scope

**Medium** (Warning with suggested fixes):

- Minor formatting inconsistencies
- Suboptimal cross-references
- Language clarity issues

**Low** (Advisory):

- Spelling errors
- Minor grammar issues
- Stylistic suggestions

### Violation Handling

**[TSP]** Documentation violations are learning opportunities, not punitive measures.

**Remediation Process**:

1. Automated check identifies violation
2. Clear explanation of issue provided
3. Suggested fix or correction offered
4. Documentation owner notified
5. Fix applied and re-validated
6. Patterns documented for team learning

---

Naming examples (good and bad): `skills/framework-authoring/resources/template-catalogue.md`.

---

## Cross-Referencing Practices

**[CA]** Clean architecture through explicit, maintained cross-references.

### Cross-Reference Standards

**Format**: Use relative paths with descriptive link text

**Good Examples**:

```markdown
See [Rule 01 - Project Organisation](01-project-organisation.rules.md) for the project-organisation
principle and profile selector. Refer to the relevant ADR in `docs-copper/architecture/adr/` for
architectural context. Review [Sprint 042 Planning](../roadmap/sprint-042/planning.md) for context.
```

**Bad Examples**:

```markdown
See Rule 01 (no link) Click here (non-descriptive) [Link](01-project-organisation.rules.md) (unclear
purpose)
```

### Cross-Reference Integrity

**Validation** **[FOC]**:

- ✅ All cross-references must resolve to existing files
- ✅ Relative paths preferred over absolute paths
- ✅ Update cross-references when files move or rename
- ✅ Detect and fix orphaned references in CI/CD

**Bidirectional References**:

- When Document A references Document B, consider adding reciprocal reference
- Maintain "Related Documents" sections for discoverability

---

## Special Documentation Types

### README Files (Exception)

**Location**: Anywhere in the codebase (exception to centralisation)

**Purpose**: Code-level documentation explaining directories, modules, components

**Standard** **[RP]**: Every code directory SHOULD contain README.md

**Required Sections**:

- Directory purpose and contents
- Key files and their roles
- Setup instructions (if applicable)
- Dependencies and relationships
- Usage examples

**Format**: Markdown with consistent structure

**Example Locations**:

```
/src/README.md
/src/api/README.md
/src/utils/README.md
/db/migrations/README.md
/scripts/backup/README.md
```

### CHANGELOG Files

**Location**: ONLY where explicitly specified by user or already existing

**Purpose**: Version history, release notes, change tracking

**Standard**: Semantic versioning (MAJOR.MINOR.PATCH) with structured entries

**Format**: Keep a Changelog with semantic versioning; the template is in
`skills/framework-authoring/resources/template-catalogue.md`.

**Governance**: User controls CHANGELOG locations; agents do NOT create new CHANGELOG files without
explicit instruction.

## Documentation Maintenance

**[SD]** Strategic documentation requires regular maintenance.

### Review Frequency

**Critical Documentation** (Quarterly review):

- Architecture decision records
- API documentation
- Security documentation
- Compliance documentation

**Important Documentation** (Bi-annual review):

- Technical design specifications
- User guides and runbooks
- Process documentation
- Integration guides

**Supporting Documentation** (Annual review):

- Historical references
- Templates
- Best practices guides

### Deprecation Process

**When Documentation Becomes Obsolete**:

1. **Mark as Deprecated**: Add deprecation notice with date
2. **Provide Alternative**: Link to current documentation
3. **Archive**: Move to `_archives/` after grace period (6 months)
4. **Update Cross-References**: Remove or redirect references

**Deprecation Notice Template**:

```markdown
> ⚠️ **DEPRECATED**: This document was deprecated on 2025-01-20. Please refer to
> [New Documentation](../path/to/new-doc.md) instead.
```

Which memory-bank file a documentation change updates: `commands/memory-update.md` (Documentation
and the memory bank).
