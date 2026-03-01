# Outage Playbook: Device Farm Degradation

## Trigger

- Widespread device allocation failures.
- Sudden spike in infra-related test failures.

## Immediate Response

1. Verify provider status page/incidents.
2. Confirm failures are infra, not test logic.
3. Isolate impacted platforms/devices.
4. Retry with reduced parallel pressure.

## Containment

- Pause non-critical lanes.
- Keep essential smoke validation on best-known stable pool.
- Mark known infra-only failures to avoid noisy regressions.

## Recovery Validation

- Device allocation succeeds consistently.
- Smoke and one regression shard pass.
- Failure signatures return to baseline.

## Follow-up

- Record incident window and affected lanes.
- Adjust retry/backoff policy if needed.
