"""
Write a synthetic CI span for one profiled scenario.

This bridges scenario-level hardware telemetry to the analyst agent's
span_metrics table before framework-level OpenTelemetry instrumentation exists.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: write_synthetic_span.py <output> <scenario> <start> <end> <traceparent>",
            file=sys.stderr,
        )
        return 2

    output, scenario, start_time, end_time, traceparent = sys.argv[1:]
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
    end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f")
    parts = traceparent.split("-")
    span_id = parts[2] if len(parts) >= 3 else "unknown"

    payload = {
        "spans": [
            {
                "span_id": span_id,
                "name": f"{scenario}.Execution",
                "start_time": start_time,
                "end_time": end_time,
                "duration_ms": round((end - start).total_seconds() * 1000, 3),
            }
        ]
    }

    Path(output).write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
