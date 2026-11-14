---
paths:
- '**/*.{py,ts,tsx,js,jsx,mjs,cjs,rs,go,java,kt,kts,scala,cs,rb,php,swift,c,h,cpp,hpp,sh,sql,tf}'
- '**/*.{html,css,scss,vue,svelte}'
- '**/Dockerfile'
---

<!-- source: kits/core/rules/02a-code.rules.md (generated) -->

**Precedence tier**: T3 (COPPER Precedence Constitution).

# Rule 02a - Code Quality, Quality Gates and Build Standards

Refines Rule 02 while a source file is open: code-smell thresholds, implementation guidelines,
performance, code organisation, quality gates and build/deployment standards. The non-negotiable
security controls and Configuration Protection are always-on in Rule 02. Scoped by `paths`
(ADR-054); its always-on anchor is Rule 02.

## Quality Assurance Standards

### Proactive Code Quality Monitoring

**[CSD] Code Smell Detection**: Actively identify and recommend refactoring for:

- Functions exceeding 30 lines → suggest modular decomposition
- Files exceeding 300 lines → recommend logical separation
- Nested conditionals beyond 2 levels → flatten complex logic
- Classes with more than 5 public methods → consider single responsibility violations

**Quality Metrics** **[TST]**:

- **Unit test coverage**: ≥80%
- **Integration test coverage**: ≥70%
- **E2E test coverage**: All critical paths
- **Max function lines**: 30
- **Max file lines**: 300
- **Max nesting levels**: 2
- **Max class methods**: 5
- **Cyclomatic complexity**: below 10 per function

### Implementation Excellence Guidelines

**[ENV] Environment Awareness**: Code must function correctly across development, test, and
production environments.

**[ORG] Organisational Clarity**: Maintain clean, well-organised codebase structure with logical
file and component organisation.

**[SCM] Script Management**: Avoid embedding one-time scripts in production files; use dedicated
utility directories.

**[MOD] Modularity Focus**: Prefer modular, reusable components over monolithic implementations.

---

## Performance & Resource Management

### Performance Excellence Requirements

**[PA] Performance Awareness**: Systematically consider computational complexity and resource usage
in all implementations.

**[RM] Resource Management**: Implement proper lifecycle management for connections, memory, and
system resources.

**[OPT] Optimisation Mindset**: Continuous performance improvement through profiling, benchmarking,
and proactive optimisation.

**[RSP] Environmental Responsibility**: Energy-efficient algorithms, minimal resource consumption.

### Architectural Patterns & Code Organisation

**API Client Generation**:

- Use OpenAPI Generator with TypeScript axios template for consistent API client creation
- Place all auto-generated code in `/src/generated` directory for clear separation

**Design Patterns**:

- Prefer composition over inheritance for flexible, maintainable code architecture
- Implement repository pattern for consistent and testable data access layers
- Follow established error handling patterns for consistency across the application

**REST Endpoint Implementation**:

- Follow established endpoint patterns consistent with the project's API framework
- Use clear package/module namespacing for endpoint organisation
- Configure service discovery via environment variables where applicable

---

## Code Quality Enforcement

Applied when code is reviewed or committed.

### Automated Quality Gates

**Pre-Commit Checks**:

- Linting (language-specific linters)
- Formatting (Prettier, Black, etc.)
- Type checking (TypeScript, mypy, etc.)
- Unit test execution
- Security scanning (dependency vulnerabilities)

**CI/CD Integration**:

- Full test suite execution
- Code coverage reporting (≥80% requirement)
- Security vulnerability scanning
- Performance regression testing
- Documentation completeness checks

### Manual Review Gates

**Code Review Requirements** **[COL]**:

- Peer review for all code changes
- Architecture review for significant changes
- Security review for authentication/authorisation changes
- Performance review for high-traffic code paths

**Review Checklist**:

- [ ] Principle codes tagged appropriately
- [ ] Test coverage meets requirements (≥80%)
- [ ] Security controls implemented correctly
- [ ] Documentation updated
- [ ] No code smells detected
- [ ] Atomic changes maintained
- [ ] Conventional commits followed

---

## Build & Deployment Standards

### Build System Requirements

**Deployment Simplicity**: Avoid unnecessary build plugin complexity; prioritise script-based,
automatable deployment processes.

**Data Management**:

- Restrict mocking and synthetic data to test environments exclusively
- NEVER use stubbing or fake data patterns in development or production environments
- Prohibit any patterns that could affect development or production with test data

---

## Accessibility and Compliance

Moved from `instructions.md` "Quality Standards (Centralised)" by US-378; the test and code-size
thresholds there are the ones above.

- **Accessibility**: WCAG 2.1 AA; colour contrast at least 4.5:1 for text and 3:1 for UI elements;
  keyboard navigation for every interactive element.
- **Compliance**: privacy per GDPR and CCPA and the regulatory context in Rule 00; security per
  OWASP Top 10 and NIST CSF; sustainability per **[RSP]** above and any commitment the identity kit
  states.
