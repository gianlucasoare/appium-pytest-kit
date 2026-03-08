# Risk Register

Review at least once per sprint.

| ID | Risk | Impact | Likelihood | Owner | Status | Mitigation |
|---|---|---|---|---|---|---|
| R-001 | Test flake growth hides regressions | High | Medium | `@owner-core` | Open | Enforce flake gates, quarantine process, weekly review |
| R-002 | Performance drift slows feedback loops | Medium | Medium | `@owner-observability` | Open | Perf telemetry + trend checks + budget thresholds |
| R-003 | Release misconfiguration publishes wrong version | High | Low | `@owner-release` | Open | Tag/version validation, guarded publish, release checklist |
| R-004 | Secrets leak in artifacts/logs | High | Medium | `@owner-ci` | Open | Artifact redaction enabled, security baseline, incident playbook |
| R-005 | xdist-specific regressions missed locally | Medium | Medium | `@owner-core` | Open | Dedicated xdist CI lane, merge-report tests |
| R-006 | Quarantine suite grows without cleanup | Medium | Medium | `@owner-actions` | Open | Quarantine owner+expiry policy, weekly cleanup |
