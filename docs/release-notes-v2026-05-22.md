# Release Notes — v2026-05-22

**Type:** New dataset
**Adds:** `data/permits/` — Saudi building permits + REGA Annual headline metrics
**Files added:** 14 (1 README + 6 gzip CSVs + 7 PDFs)
**Total size:** ~66 MB (17 MB CSV + 49 MB PDF)

## Summary

First release of the consolidated **Saudi Building Permits Dataset**.
Combines building permit issuance records from Saudi municipal
publishers (Amanas) on the Saudi Open Data Portal, KAPSARC's 33-year
historical series (1987–2019), Riyadh municipality news, and headline
metrics extracted from REGA's Annual Reports (2018–2024).

This is the supply-side counterpart to the existing transaction data
in `rega/` (sales/rental indicators) — permits lead transactions by
6–24 months, making this useful as a forward indicator for market
activity **in the regions with strong coverage**.

> **Coverage is uneven.** Of 14 amanas in our collection pipeline,
> only **7 produce substantial modern data**: Medina, Tabuk, Eastern
> Province (2025 only), Al-Bahah, Qassim, Al-Jouf, Al-Ahsa. **Riyadh
> has essentially no modern coverage** — 1,022 KAPSARC rows ending
> 2019, plus 2 alriyadh-news 2024 aggregates. See the "Coverage by
> region" section below and `data/permits/README.md` for the full
> region-by-region breakdown.

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

## Coverage by region

Modern per-permit coverage (`permits_raw`, 191,063 rows, 2014–2026) is
**concentrated in 7 amanas**:

| Region | `permits_raw` rows | Date span | Notes |
|---|---:|---|---|
| Medina | 67,644 | 1991–2025 | 35% of all raw — dominant publisher |
| Tabuk | 39,040 | 1983–2026 | Long history |
| Eastern Province | 29,398 | **2025 only** | Recently onboarded |
| Al-Bahah | 21,399 | 1977–2026 | Long history |
| Qassim | 13,094 | 1977–2025 | Long history |
| Al-Jouf | 11,585 | 1971–2026 | Includes 2 `year=2064` errors |
| Al-Ahsa | 8,903 | 2003–2026 | Sub-unit of Eastern Province |

**Symbolic in `permits_aggregate`:** Jeddah (4 rows, 2021–2024), Asir
(2 rows, 2025).

**Modern coverage absent or minimal:** Riyadh, Makkah (city/region),
Hail, Northern Borders, Jazan, Najran, Sakaka.

**KAPSARC historical (`permits_historical`)** is the only universal
source: all 13 administrative regions at ~1,008–1,026 rows each,
1987–2019. This is the **only Riyadh data** in the dataset (1,022
historical rows ending 2019, plus 2 alriyadh-news 2024 aggregates).

## Sources

- **Saudi Open Data Portal** (`open.data.gov.sa`) — pipeline configured
  for 14 amana publishers + KAPSARC. **As of this release, 7 of 14
  amanas produce substantial data.** The other 7 are either silent
  publishers, publish outside our permit-keyword filter, or have very
  few cataloged datasets. See `known_permit_resources.csv.gz`.
- **KAPSARC** — 33-year (1987-2019) cross-region historical permit series. Only universal-coverage source.
- **alriyadh.gov.sa** — Riyadh municipality 2024 weekly permit
  summaries. Currently contributes 2 rows in `permits_historical`.
- **REGA Annual Reports** — 7 PDFs cached in `data/permits/pdfs/`.

## Use cases (matched to coverage reality)

**Where this release is strong:**

- Supply-side housing/commerce signals for Medina, Tabuk, Al-Bahah,
  Qassim, Al-Jouf, Al-Ahsa, and Eastern Province (2025+).
- Long-horizon (1987–2019) kingdom-wide residential vs commercial
  trends via `permits_historical`.
- Subdivision pipeline as a 12–24 month leading indicator.
- Off-plan supply forecasting via `rega_annual_metrics` (Wafi off-plan
  units licensed: 37,244 in 2023 → 104,747 in 2024).

**Where this release is weak or silent:**

- **Riyadh modern (2020+) — essentially no data** (2 alriyadh-news rows
  is the entirety of post-2019 Riyadh coverage in this release).
- Makkah, Jeddah, Asir, Hail, Northern Borders, Jazan, Najran, Sakaka
  modern coverage.

## Schema

See [`data/permits/README.md`](../data/permits/README.md) for full
column-by-column schema documentation across all six tables, plus a
detailed Coverage table.

## Known limitations

- **48,605 `permits_raw` rows have NULL `issued_date`** — upstream
  sources publish month-bucket aggregates without point-in-time dates.
- **Riyadh has no useful modern coverage** — see Coverage section above.
- **Eastern Province modern coverage starts in 2025** — no deep
  backfill yet.
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
