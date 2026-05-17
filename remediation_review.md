# Remediation Fix Report

Date: 2026-05-17

## Completed Fixes

| Finding | Status | Fix Applied |
|---|---:|---|
| Mac validation does not block MinIO upload | Fixed | Removed `if: always()` from MinIO upload steps so failed validation blocks offload |
| Truncated runs are still accepted | Fixed | Duration guards now exit `1` on `truncated=true`; analyst also rejects truncated ZIPs |
| Parser validation warnings do not fail conversion | Fixed | `parse_powermetrics.py` now exits `1` when `validation_issues` is non-empty |
| Manual Mac uploader path is wrong | Fixed | `upload_mac_data.py` now uploads to `raw-telemetry/{project_name}/{run_id}/{scenario}.zip` |
| SQLite UNIQUE migration is incomplete | Fixed | Added table rebuild migration for project-scoped UNIQUE constraints |
| Generated cache file present | Fixed | Removed `scripts/__pycache__/` |

## Confirmed Fixed

| Fix | Status |
|---|---:|
| Composer profiler cap raised to `900s` on both platforms | Fixed |
| PHPUnit profiler cap raised to `1500s` on both platforms | Fixed |
| Duration guard added to Composer, DB migration, and PHPUnit | Fixed |
| Mac duration guard added | Fixed |
| Mac validation exits `1` on missing or empty CSV | Fixed |
| Feasibility-study `parse_powermetrics.py` synced | Fixed |
| `hardware_metadata.json` uploaded to MinIO | Fixed |
| Mac CPU metadata uses total physical cores and records P/E cores | Fixed |
| Existing SQLite DBs can migrate to project-scoped UNIQUE constraints | Fixed |

## Bottom Line

The pipeline now fails fast on conversion validation errors and profiler truncation. MinIO upload is gated behind successful validation, and the analyst rejects truncated ZIPs if they are uploaded manually.
