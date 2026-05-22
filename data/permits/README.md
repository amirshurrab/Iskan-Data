# Saudi Building Permits Dataset (تصاريح البناء)

[![Data: KSA Open Data License](https://img.shields.io/badge/data-KSA%20Open%20Data%20License-green.svg)](../../LICENSE-DATA.md)

Building permit issuance + REGA Annual Report headline metrics, consolidated from multiple Saudi public sources into a single queryable dataset.

**Coverage at a glance:**

| Table | Rows | Period | Sources |
|---|---:|---|---|
| `permits_raw.csv.gz` | 191,063 | 1971–2026 | Per-permit records from 14 amana portals + KAPSARC |
| `permits_aggregate.csv.gz` | 16,591 | 2014–2025 | Quarterly / annual aggregates by region × municipality × permit action |
| `permits_historical.csv.gz` | 14,276 | 1987–2019 | KAPSARC 33-year historical series (14 regions × 8 building types × 6 indicators) |
| `subdivisions_aggregate.csv.gz` | 215 | 2014–2025 | Subdivision plot creation (land-development pipeline indicator) |
| `known_permit_resources.csv.gz` | 113 | n/a | Catalog of source resources used (Saudi Open Data dataset IDs, KAPSARC, alriyadh.gov.sa) |
| `rega_annual_metrics.csv.gz` | 24 | 2018–2024 | REGA Annual Report headline metrics — Wafi off-plan licenses, practitioners, platforms, registry beneficiaries, rental contracts |

Source PDFs for the REGA Annual Reports are in [`pdfs/`](pdfs/).

---

## What is this data?

Two distinct things bundled in one folder:

1. **Building permits** (the bulk) — records of construction/renovation permits issued by Saudi municipal authorities (Amanas). Each `permits_raw` row is one permit with issued date, region, municipality, permit action (new/extension/renovation), deed type, and building use. Aggregates roll these up by region × time period.
2. **REGA Annual headline metrics** — selected Wafi off-plan licensing, practitioner counts, platform adoption, and rental contract figures pulled by hand from the regulator's annual reports (2018–2024). NOT building permits — REGA's own regulatory output stats.

The two are bundled because both answer the broader question *"how much real-estate development activity is happening in Saudi Arabia?"* — permits are the supply-side leading signal, REGA metrics are the regulatory-output trailing signal.

---

## Use cases

This dataset was assembled to support questions like:

- **Supply-side housing/commerce signals.** How many permits are issued per quarter in Riyadh / Jeddah / Eastern Province? Is residential construction accelerating or slowing?
- **Regional comparison.** Which amanas are issuing the most permits relative to their population? Where is the gap between permit issuance and actual completed projects?
- **Year-over-year trends.** With KAPSARC's 1987-2019 historical series + recent collectors, the residential permit series now spans 39 years — enough for long-horizon trend analysis.
- **Residential vs commercial mix.** `permits_raw.building_use` + `permits_historical.building_type` let you separate housing supply from commercial supply over time.
- **Subdivision pipeline indicator.** `subdivisions_aggregate` tracks raw-land subdivision approvals — a leading indicator that precedes building permits by 12-24 months.
- **Cross-source coverage gaps.** `known_permit_resources` documents which sources we polled — useful for auditing what's missing (e.g., several smaller amanas publish irregularly or not at all; Riyadh has a notable 2020-2023 gap).
- **Cross-reference with [`../../rega/`](../../rega/) sales transactions.** When permits surge in a region 6-12 months before sales activity picks up, that's a measurable supply-led market signal. Joining these on `region_ar` + `year`/`quarter` lets you test it.
- **Off-plan supply forecasting.** `rega_annual_metrics` captures Wafi off-plan project licenses + units — a forward indicator of housing units that will hit the market 2-4 years out.

---

## Schema

All CSVs are gzip-compressed (`.csv.gz`). Decompress with `gunzip`, or read directly in pandas (`pd.read_csv('permits_raw.csv.gz')`) / DuckDB (`SELECT * FROM read_csv('permits_raw.csv.gz')`).

### `permits_raw`

One row per permit. Heterogeneous shape across sources — some publish per-permit detail, others publish only aggregates (those land in `permits_aggregate` instead).

| Column | Type | Notes |
|---|---|---|
| `raw_id` | int | Surrogate key |
| `source` | text | Source identifier (`saudi-open-data`, `kapsarc-historical`, `alriyadh-news-2024`, etc.) |
| `source_dataset_id` | text | Upstream dataset ID for traceability |
| `source_resource_id` | text | Upstream resource ID within the dataset |
| `region_ar` | text | Saudi region name in Arabic |
| `municipality_ar` | text | Municipality / amana name in Arabic |
| `issued_date` | text | ISO `YYYY-MM-DD` or NULL when source publishes month-only |
| `permit_action` | text | New / extension / renovation / demolition (source-specific vocabulary) |
| `deed_type` | text | Land deed classification at permit time |
| `building_use` | text | Residential / commercial / industrial / mixed (source-specific) |
| `raw_row_json` | text | Original row as JSON — for fields not normalized into columns |
| `captured_at` | text | ISO timestamp of ingest |
| `row_hash` | text | SHA-256 of the upstream row (deduplication key) |

### `permits_aggregate`

Quarterly / annual rollups by region + municipality + permit action, for sources that publish only aggregates.

| Column | Type | Notes |
|---|---|---|
| `agg_id` | int | Surrogate key |
| `source` | text | Source identifier |
| `region_ar` | text | Saudi region (Arabic) |
| `year` | int | Gregorian year |
| `quarter` | int | 1–4, or NULL for annual-only |
| `month` | int | 1–12, or NULL |
| `municipality_ar` | text | Municipality (Arabic), or NULL for region-level |
| `permit_action` | text | Action category |
| `permit_count` | int | Number of permits issued in the bucket |
| `captured_at` | text | ISO timestamp |

### `permits_historical`

KAPSARC's 33-year cross-region permit series (1987–2019). Long form: one row per (year, region, building_type, indicator).

| Column | Type | Notes |
|---|---|---|
| `hist_id` | int | Surrogate key |
| `source` | text | Always `kapsarc-1987-2019` |
| `year` | int | Gregorian |
| `region` | text | English region label as published (e.g. `Riyadh`, `Madinah`, `Grand Total`) |
| `building_type` | text | `Residential`, `Commercial`, `Total`, etc. |
| `indicator` | text | `Number of Permits`, `Total Area of Building (S.M.)`, etc. |
| `indicator_value` | real | Value (units depend on `indicator`); NULL for missing cells |
| `captured_at` | text | ISO timestamp |

### `subdivisions_aggregate`

| Column | Type | Notes |
|---|---|---|
| `div_id` | int | Surrogate key |
| `source`, `region_ar`, `year`, `quarter` | — | As above |
| `plot_count` | int | Number of plots created |
| `plot_area_sqm` | real | Total area (m²) |
| `plot_type` | text | Residential / commercial / mixed |
| `ownership_type` | text | Public / private |

### `known_permit_resources`

| Column | Type | Notes |
|---|---|---|
| `resource_id` | text | Upstream resource identifier |
| `source` | text | Source family |
| `dataset_id` | text | Parent dataset ID |
| `detected_shape` | text | Detected CSV shape (annual_total / quarterly_per_region / per_permit / etc.) |
| `parsed_at` | text | ISO timestamp |
| `row_count` | int | Rows ingested from this resource |
| `error_msg` | text | NULL on success, else parser error |

### `rega_annual_metrics`

Hand-extracted metrics from REGA Annual Reports — only metrics where the value could be visually confirmed against the headline card in the source PDF.

| Column | Type | Notes |
|---|---|---|
| `metric_id` | int | Surrogate key |
| `year` | int | Report year |
| `metric` | text | Canonical key (`wafi_offplan_licenses_count`, `practitioners_total`, etc.) |
| `indicator_value` | real | Value as extracted |
| `unit` | text | `count`, `sqm`, `SAR`, `percent` |
| `raw_label_ar` | text | Original Arabic descriptor (audit aid) |
| `page_hint` | int | Approximate PDF page number (audit aid) |

---

## Sources

- **Saudi Open Data Portal** (`open.data.gov.sa`) — 14 amana publishers (Riyadh, Eastern Province, Madinah, Makkah, Qassim, Asir, Tabuk, Hail, Northern Borders, Jazan, Najran, Al Bahah, Al Jouf, Sakaka) + KAPSARC.
- **KAPSARC** — 33-year (1987-2019) cross-region historical permit series.
- **alriyadh.gov.sa** (الرياض) — Riyadh municipality 2024 weekly permit summaries, scraped from news archive.
- **REGA Annual Reports** — `rega.gov.sa/about-us/board-decisions-and-reports` — 7 PDFs (2018-2024) cached in [`pdfs/`](pdfs/).

---

## Limitations & caveats

- **48,605 `permits_raw` rows have NULL `issued_date`.** Some upstream sources publish month-bucket aggregates as individual rows without a single issued date. Treat these as month/quarter-bucket records, not point-in-time events.
- **2 rows show `2064` as the year** — almost certainly Hijri/Gregorian transcription errors in the upstream. Filter these for time-series work.
- **Riyadh has a 2020-2023 coverage gap.** The Saudi Open Data portal doesn't publish Riyadh per-permit records for that period; we partially filled it via the alriyadh-news 2024 scraper but the gap remains visible.
- **Permit action vocabulary varies by source.** No global cleanup pass yet. `permit_action` in `permits_raw` reflects the upstream label.
- **REGA Annual metrics are hand-verified only.** We extracted ~3-4 metrics per year that could be visually confirmed against the report's headline cards. The reports contain many more numbers; full extraction is deferred until the consumer use-case justifies the manual cost.
- **`permits_aggregate` and `permits_raw` can double-count if joined naively.** Aggregates were published independently of per-permit records; many regions appear in BOTH. Pick one for any given (region, period) query — usually `permits_raw` if available, else `permits_aggregate`.
- **`known_permit_resources` shows 113 resources audited; some have `error_msg` set** indicating parse failure. Those resources are NOT represented in the other tables.

---

## Update cadence

Permits collectors run weekly to monthly depending on source — Saudi Open Data portal poll, alriyadh-news scan, KAPSARC refresh. See the repo's [`CHANGELOG.md`](../../CHANGELOG.md) for release-level updates. The collection code lives in a private staging repository; this public release is a periodic snapshot.

---

## Citation

If you use this data in research or publications, please cite:

```
Saudi Real Estate Open Data — Building Permits Dataset
https://github.com/civillizard/Saudi-Real-Estate-Data
Snapshot: v2026-05-22
```

Underlying data is the property of its respective publishers (Saudi Open Data Portal publishers, KAPSARC, alriyadh.gov.sa, REGA). This release is a consolidation and reformatting only.
