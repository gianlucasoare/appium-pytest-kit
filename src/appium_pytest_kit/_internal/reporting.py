"""Minimal optional reporting helpers for pytest runs."""


import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SessionReportCollector:
    """Collects basic test outcomes and writes a small JSON summary."""

    output_dir: Path
    output_filename: str = "summary.json"
    records: list[dict[str, Any]] = field(default_factory=list)

    def record(self, report: Any) -> None:
        """Capture a single test call-phase report."""

        if getattr(report, "when", None) != "call":
            return
        self.records.append(
            {
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "duration": report.duration,
            }
        )

    def flush(self) -> Path:
        """Persist report summary to disk and return the file path."""

        self.output_dir.mkdir(parents=True, exist_ok=True)
        totals = {"passed": 0, "failed": 0, "skipped": 0}
        for row in self.records:
            outcome = str(row["outcome"])
            totals[outcome] = totals.get(outcome, 0) + 1

        payload = {
            "totals": totals,
            "tests": self.records,
        }
        output_path = self.output_dir / self.output_filename
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path
