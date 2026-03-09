# Script Rules

This file applies to `scripts/**`.

- Treat release and quality-gate scripts as CI-facing interfaces; keep arguments and outputs stable unless the workflow changes in the same change set.
- If a script participates in publish or release work, enforce the mandatory preflight sequence before release is considered ready.
- Keep changelog automation aligned with `python3 scripts/update_changelog.py --version X.Y.Z`.
- Start failure analysis from the first real traceback and add regression coverage when a script bug is fixed.
- Keep xdist and artifact-processing logic tolerant of missing partial files and idempotent across reruns.
- Prefer artifact redaction and avoid emitting sensitive environment data.
- Never hardcode credentials or commit real secrets; use environment variables or CI secret stores.
