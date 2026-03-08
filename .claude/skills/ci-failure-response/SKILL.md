---
name: ci-failure-response
description: Handle CI failures with fast evidence-based diagnosis, targeted fixes, and recurrence prevention.
---

# CI Failure Response

## Use This Skill When

- A CI lane fails
- xdist-specific failures occur
- Reporting or artifact issues arise in CI
- Recurring CI instability needs resolution

## Procedure

1. Identify failing lane and first true error (not the summary line)
2. Classify root cause: flaky test, code regression, environment, or workflow config
3. Reproduce locally with equivalent command:
   - Main lane: `python3 -m pytest -q -m "not quarantine"`
   - xdist lane: `python3 -m pytest -q -n 2 -m "not quarantine"`
   - Quarantine: `python3 -m pytest -q -m quarantine`
4. Patch with targeted regression test
5. Re-run lane-equivalent checks locally
6. For xdist/reporting failures: validate missing-file tolerance and controller vs worker paths
7. Capture lessons in ADR or playbook if recurring

## xdist-Specific Checks

- Never assume report files exist per worker
- Use safe existence checks before reading worker artifacts
- Treat controller and worker responsibilities separately
- File merge logic must be idempotent and resilient to missing partial files

## Definition of Done

- Root cause confirmed
- Fix validated in affected lane
- Recurrence risk reduced (regression test or config hardening)
