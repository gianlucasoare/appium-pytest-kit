# Outage Playbook: Appium Server Instability

## Trigger

- Frequent `session not created` / connection reset errors.
- Health endpoint failures across multiple jobs.

## Immediate Response

1. Confirm server reachability and logs.
2. Check port collisions and orphan processes.
3. Validate driver/Appium version compatibility.
4. Re-run a minimal smoke test.

## Containment

- Restart managed Appium service.
- Reduce parallelism temporarily if resource constrained.
- Route critical checks to a single stable lane.

## Recovery Validation

- Smoke lane passes.
- xdist lane passes.
- No new systemic session-creation errors.

## Follow-up

- Capture root cause and preventive action.
- Update CI config or playbooks if needed.
