# Release Notes — v2026-05-22

**Type:** New dataset
**Adds:** `data/permits/` — Saudi building permits + REGA Annual headline metrics
**Files added:** 14 (1 README + 6 gzip CSVs + 7 PDFs)
**Total size:** ~66 MB (17 MB CSV + 49 MB PDF)

## Summary

First release of the consolidated **Saudi Building Permits Dataset**.
Combines building permit issuance records from 14 Saudi municipal
publishers (Amanas) on the Saudi Open Data Portal, KAPSARC's 33-year
historical series (1987–2019), Riyadh municipality news, and headline
metrics extracted from REGA's Annual Reports (2018–2024).

This is the supply-side counterpart to the existing transaction data
in `rega/` (sales/rental indicators) — permits lead transactions by
6–24 months, making this useful as a forward indicator for market
activity.

## What's new

### `data/permits/csv/` (6 gzip-compressed CSVs)

| File | Rows | Period | Description |
|---|---:|---|---|
| `permits_raw.csv.gz` | 191,063 | 1971–2026 | Per-permit records (14 amanas + KAPSARC) |
| `permits_aggregate.csv.gz` | 16,591 | 2014–2025 | Quarterly / annual rollups by region × municipality |
| `permits_historical.csv.gz` | 14,276 | 1987–2019 | KAPSARC 33-year cross-region series |
| `subdivisions_aggregate.csv.gz` | 215 | 2014–2025 | Subdivision plot creation (land-development pipeline) |
| `known_permit_resources.csv.gz` | 113 | n/a | Catalog of source resources audited |
| `rega_annual_metrics.csv.gz` | 24 | 2018–2024 | Hand-verified REGA Annual headline metrics |

All CSVs are gzip-compressed (`.csv.gz`). Decompress with `gunzip`,
or read directly in pandas / DuckDB (both support gzip transparently).

### `data/permits/pdfs/` (7 REGA Annual Reports)

Source PDFs for the 24 entries in `rega_annual_metrics.csv.gz`:

- `rega-annual-2018.pdf` (2.7 MB)
- `rega-annual-2019.pdf` (4.0 MB)
- `rega-annual-2020.pdf` (7.3 MB)
- `rega-annual-2021.pdf` (4.5 MB)
- `rega-annual-2022.pdf` (5.7 MB)
- `rega-annual-2023.pdf` (24.6 MB — richer infographic layout)
- `rega-annual-2024.pdf` (3.3 MB)

Bundling source PDFs alongside the parsed metrics lets consumers
verify values without re-downloading from `rega.gov.sa`.

## Sources

- **Saudi Open Data Portal** (`open.data.gov.sa`) — 14 amana publishers
  + KAPSARC.
- **KAPSARC** — 33-year (1987-2019) cross-region historical permit series.
- **alriyadh.gov.sa** — Riyadh municipality 2024 weekly permit
  summaries.
- **REGA Annual Reports** — 7 PDFs cached in `data/permits/pdfs/`.

## Use cases

- Supply-side housing/commerce signals (permits per quarter by region)
- Regional comparison across the 14 amanas
- Year-over-year trends — 39-year residential series via KAPSARC +
  recent collectors
- Residential vs commercial mix over time
- Subdivision pipeline as a 12–24 month leading indicator
- Cross-reference with `rega/` sales data: do permit surges precede
  sales activity? Join on `region_ar` + `year`/`quarter`
- Off-plan supply forecasting via `rega_annual_metrics`
  (Wafi off-plan units licensed: 37,244 in 2023 → 104,747 in 2024)

## Schema

See [`data/permits/README.md`](../data/permits/README.md) for full
column-by-column schema documentation across all six tables.

## Known limitations

- **48,605 `permits_raw` rows have NULL `issued_date`** — upstream
  sources publish month-bucket aggregates without point-in-time dates.
- **Riyadh 2020–2023 coverage gap** — Saudi Open Data Portal doesn't
  publish Riyadh per-permit records for that period.
- **2 rows show `year=2064`** — Hijri/Gregorian transcription errors
  in upstream. Filter for time-series work.
- **`permits_aggregate` and `permits_raw` can double-count if joined
  naively** — pick one for any given (region, period) query.
- **REGA Annual metrics are hand-verified only** — ~3-4 metrics per
  year visually confirmed against headline cards. Full extraction
  deferred until use-case justifies the cost.

Full caveats in [`data/permits/README.md`](../data/permits/README.md).

## How to fetch

```bash
# All CSVs
curl -O https://raw.githubusercontent.com/civillizard/Saudi-Real-Estate-Data/main/data/permits/csv/permits_raw.csv.gz
curl -O https://raw.githubusercontent.com/civillizard/Saudi-Real-Estate-Data/main/data/permits/csv/permits_aggregate.csv.gz
# ... etc

# Or clone for everything (including PDFs)
git clone https://github.com/civillizard/Saudi-Real-Estate-Data.git
```

## Citation

```
Saudi Real Estate Open Data — Building Permits Dataset
https://github.com/civillizard/Saudi-Real-Estate-Data
Snapshot: v2026-05-22
```
