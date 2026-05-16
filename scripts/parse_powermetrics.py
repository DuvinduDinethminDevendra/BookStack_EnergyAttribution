"""
parse_powermetrics.py
Converts macOS powermetrics text output → AMD µProf compatible timechart.csv

The output CSV must be EXACTLY compatible with analyst_agent.py:
  - Header: "PROFILE RECORDS," marker followed by column headers
  - Timestamps: H:M:S:mmm wall-clock format (matching AMD uProf format)
  - Power column: "Package Power (W)" matching find_power_column() pattern
  - Power values: in Watts (converted from mW)

The critical requirement is that timechart timestamps are WALL-CLOCK times,
not zero-based offsets, because deconvolve() in analyst_agent.py matches them
against exec_start/exec_end times from timestamps.csv.

Usage: python3 scripts/parse_powermetrics.py <run_id>
"""

import re
import sys
from pathlib import Path
from datetime import datetime

SCENARIOS = ["Idle", "Composer_Install", "DB_Migration", "PHPUnit_Tests"]


def parse_power_samples(text: str) -> list[dict]:
    """
    Extract CPU Power (mW) and the wall-clock timestamp from each sample block.

    Each powermetrics sample block starts with a line like:
      *** Sampled system activity (Fri May 15 09:51:40 2026 +0530) (103.01ms elapsed) ***

    And contains a line like:
      CPU Power: 335 mW

    Returns list of dicts: { 'timestamp': datetime, 'watts': float }
    """
    samples = []

    # Split into sample blocks using the *** Sampled ... *** marker
    # Pattern for the header line with timestamp
    header_pattern = re.compile(
        r"\*\*\* Sampled system activity \((.+?)\) \(\d+\.\d+ms elapsed\) \*\*\*"
    )
    # Pattern for CPU Power line
    power_pattern = re.compile(r"CPU Power:\s+([\d.]+)\s+mW")

    # Split text into blocks by the *** marker
    blocks = re.split(r"(?=\*\*\* Sampled system activity)", text)

    for block in blocks:
        header_match = header_pattern.search(block)
        power_match = power_pattern.search(block)

        if header_match and power_match:
            # Parse timestamp: "Fri May 15 09:51:40 2026 +0530"
            ts_str = header_match.group(1)
            # Remove timezone offset for parsing, handle it separately
            # Format: "Fri May 15 09:51:40 2026 +0530"
            try:
                # Strip the timezone part for simple parsing
                # We only need H:M:S:mmm for the timechart
                ts_parts = ts_str.rsplit(" ", 1)  # Split off "+0530"
                ts_clean = ts_parts[0]  # "Fri May 15 09:51:40 2026"
                ts = datetime.strptime(ts_clean, "%a %b %d %H:%M:%S %Y")
            except ValueError:
                continue

            watts = float(power_match.group(1)) / 1000.0  # mW → W
            samples.append({"timestamp": ts, "watts": watts})

    return samples


def generate_timechart_csv(samples: list[dict]) -> str:
    """
    Generate AMD µProf-compatible timechart CSV with WALL-CLOCK timestamps.

    AMD uProf format:
      PROFILE RECORDS,
      RecordId,Timestamp,socket0-package-power,...
      1,20:58:19:282,    9.27,...

    Our simplified Mac format (compatible with analyst_agent.py):
      PROFILE RECORDS,
      Timestamp,Package Power (W)
      9:51:40:000,0.2330

    The Timestamp column uses H:M:S:mmm wall-clock format.
    analyst_agent.py's parse_timechart_timestamp() parses this as:
      parts = ts.split(":") → h, m, s, ms
    analyst_agent.py's deconvolve() converts exec_start/exec_end to:
      timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms//1000)
    Then matches: df["_td"] >= exec_start_td & df["_td"] <= exec_end_td

    CRITICAL: Since powermetrics only gives second-level precision in its
    header timestamps, we use the sample index to estimate sub-second offsets
    when multiple samples share the same second.
    """
    lines = ["PROFILE RECORDS,", "Timestamp,Package Power (W)"]

    # Group samples by their second-level timestamp to distribute
    # millisecond offsets within each second
    if not samples:
        return "\n".join(lines) + "\n"

    # Track how many samples we've seen for each second
    second_counts: dict[str, int] = {}

    for sample in samples:
        ts = sample["timestamp"]
        watts = sample["watts"]

        # Create a key for this second
        sec_key = ts.strftime("%H:%M:%S")

        if sec_key not in second_counts:
            second_counts[sec_key] = 0
        else:
            second_counts[sec_key] += 1

        # Estimate millisecond offset: each sample within the same second
        # is ~100ms apart
        ms_offset = second_counts[sec_key] * 100

        # Format as H:M:S:mmm (matching AMD uProf format)
        # Note: AMD uses non-zero-padded values, e.g., "21:6:19:744"
        timestamp = f"{ts.hour}:{ts.minute}:{ts.second}:{ms_offset:03d}"
        lines.append(f"{timestamp},{watts:.4f}")

    return "\n".join(lines) + "\n"


def process_run(run_id: str):
    """Process all scenarios for a given Mac run ID."""
    base = Path(__file__).parent.parent / "ResearchData" / "cpudata" / run_id

    if not base.exists():
        print(f"ERROR: Run directory not found: {base}")
        sys.exit(1)

    for scenario in SCENARIOS:
        scenario_dir = base / scenario
        raw_file = scenario_dir / "power_data.txt"
        output_file = scenario_dir / "timechart.csv"

        if not raw_file.exists():
            print(f"  ⚠️  Skipping {scenario}: {raw_file} not found")
            continue

        text = raw_file.read_text()
        samples = parse_power_samples(text)

        if not samples:
            print(f"  ❌ {scenario}: No power samples found!")
            continue

        csv_content = generate_timechart_csv(samples)
        output_file.write_text(csv_content)

        # Show time range for verification
        first_ts = samples[0]["timestamp"].strftime("%H:%M:%S")
        last_ts = samples[-1]["timestamp"].strftime("%H:%M:%S")
        print(f"  ✅ {scenario}: {len(samples)} samples ({first_ts} → {last_ts}) → {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/parse_powermetrics.py <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]
    print(f"Parsing powermetrics data for run: {run_id}")
    process_run(run_id)
    print("\nDone! Now run: python3 scripts/upload_mac_data.py", run_id)
