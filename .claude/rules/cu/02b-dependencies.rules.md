---
paths:
- '**/{pyproject.toml,package.json,requirements*.txt,Cargo.toml,uv.lock,package-lock.json}'
- '**/{yarn.lock,pnpm-lock.yaml,poetry.lock,Pipfile,Pipfile.lock,setup.py,setup.cfg,Cargo.lock}'
- '**/{go.mod,go.sum,Gemfile,Gemfile.lock,pom.xml,build.gradle,build.gradle.kts,composer.json}'
---

<!-- source: kits/core/rules/02b-dependencies.rules.md (generated) -->

**Precedence tier**: T3 (COPPER Precedence Constitution).

# Rule 02b - Dependency Management

Refines Rule 02 while a dependency manifest or lock file is open. Scoped by `paths` (ADR-054); its
always-on anchor is Rule 02, which also requires this rule before a dependency is added by a
package-manager command (a command does not load it on its own).

## Comprehensive Dependency Management

**[QSR] Quarterly Security Review**: Conduct comprehensive vulnerability assessment of all
third-party dependencies.

**[PKV] Package Verification**: Prioritise signed or cryptographically verified packages for
security assurance.

**[DEH] Dependency Hygiene**: Remove unused or outdated dependencies promptly to reduce attack
surface.

**[DCH] Dependency Change Documentation**: Document all dependency updates with rationale in project
changelog.
