---
paths:
- '**/{architecture,adr,ADR}/**'
---

<!-- source: kits/core/rules/05a-adr.rules.md (generated) -->

**Precedence tier**: T4 (COPPER Precedence Constitution).

# Rule 05a - Architectural Decision Records

Loaded while an architecture or ADR file is touched. Scoped by `paths` (ADR-054); its always-on
anchor is Rule 05.

## Architectural Decision Records (ADRs)

**[RAT] [TR]** All significant architectural decisions MUST be documented via ADRs:

- Use the owning skill resource from `skills/architecture-documentation/resources/adr-template.md`
- Under `EP-101` and `US-112`, this should later move to the owning `cu:architecture-documentation`
  skill resource
- Store in `/architecture/ADR/`
- Include context, decision, consequences, alternatives
- Link related ADRs

**Quality Standards**:

- ADR for all architecture patterns adopted
- Peer review required
- Regular ADR review (quarterly)
