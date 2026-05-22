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

- **Supply-side housing/commerce signals (where coverage is strong).** Permit issuance trajectories for Medina, Tabuk, Al-Bahah, Qassim, Al-Jouf, Al-Ahsa, and Eastern Province (2025 onward). These 7 amanas have publisher-grade coverage with quarterly/annual cadence. See the Coverage table below for spans.
- **Long-horizon historical analysis (kingdom-wide).** KAPSARC's 1987–2019 series in `permits_historical` is the only cross-region source covering all 13 administrative regions — the right table for 33-year residential vs commercial trends, regional rankings over time, and pre-2020 baselines.
- **Residential vs commercial mix.** `permits_raw.building_use` + `permits_historical.building_type` let you separate housing supply from commercial supply over time (for the regions where modern data exists).
- **Subdivision pipeline indicator.** `subdivisions_aggregate` tracks raw-land subdivision approvals — a leading indicator that precedes building permits by 12-24 months.
- **Cross-source coverage audit.** `known_permit_resources` documents which sources we polled across 12 amanas — useful for understanding what's published vs what's silent.
- **Cross-reference with [`../../rega/`](../../rega/) sales transactions** for the covered regions. When permits surge in (e.g.) Medina 6-12 months before sales activity picks up there, that's a measurable supply-led market signal.
- **Off-plan supply forecasting (kingdom-wide).** `rega_annual_metrics` captures Wafi off-plan project licenses + units — a forward indicator of housing units that will hit the market 2-4 years out.

**Not well-supported by this release:** Riyadh modern (2020+) — only 2 alriyadh-news rows + KAPSARC's pre-2020 history. Makkah, Jeddah, Asir, Hail, Northern Borders, Jazan, Najran, Sakaka — zero-or-symbolic modern coverage. If your question depends on Riyadh recent activity, this release will not answer it.

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

## Coverage by region — what's actually in here

Modern per-permit coverage (`permits_raw`, 191,063 rows) is **uneven across the kingdom**. Seven amanas contribute substantial data; the rest are minimally represented or absent. For historical context (1987–2019), KAPSARC's `permits_historical` is the only source with universal 13-region coverage.

**`permits_raw` (modern per-permit, ~2014–2026):**

| Region | Rows | Date span | Notes |
|---|---:|---|---|
| Medina (المدينة المنورة) | 67,644 | 1991–2025 | 35% of all raw — dominant publisher |
| Tabuk (تبوك) | 39,040 | 1983–2026 | Long history |
| Eastern Province (المنطقة الشرقية) | 29,398 | **2025 only** | Recently onboarded; deep backfill not yet published |
| Al-Bahah (الباحة) | 21,399 | 1977–2026 | Long history |
| Qassim (القصيم) | 13,094 | 1977–2025 | Long history |
| Al-Jouf (الجوف) | 11,585 | 1971–2026 | Long history (incl. 2 `year=2064` transcription errors) |
| Al-Ahsa (الأحساء) | 8,903 | 2003–2026 | Sub-unit of Eastern Province |

**`permits_aggregate` adds only token coverage for two more regions** (Jeddah: 4 rows, 2021–2024; Asir: 2 rows, 2025).

**Not in modern coverage:** Riyadh, Makkah (Mecca city/region beyond Jeddah's 4 rows), Hail, Northern Borders, Jazan, Najran, Sakaka. Sources for several of these are configured in our collection pipeline (see `known_permit_resources.csv.gz`) but the upstream publishers have not yet released substantial datasets, or what they publish doesn't pass our permit-keyword filter.

**`permits_historical` (KAPSARC, 1987–2019, 14,274 rows + 2 alriyadh-news 2024 rows):**

All 13 administrative regions are represented at ~1,008–1,026 rows each (one row per year × building-type × indicator). This is currently the **only source of long-horizon Riyadh data** in the dataset — 1,022 rows for Riyadh, all pre-2020.

---

## Sources

- **Saudi Open Data Portal** (`open.data.gov.sa`) — pipeline configured for 14 amana publishers (Riyadh, Eastern Province, Madinah, Makkah, Qassim, Asir, Tabuk, Hail, Northern Borders, Jazan, Najran, Al Bahah, Al Jouf, Sakaka) + KAPSARC. **As of this release, only 7 of those amanas have produced substantial data** — see the Coverage table above. The other 7 are either silent publishers, publish only outside our permit-keyword filter, or have very small dataset counts. `known_permit_resources.csv.gz` documents the full audit.
- **KAPSARC** — 33-year (1987-2019) cross-region historical permit series. Only universal-coverage source in the dataset.
- **alriyadh.gov.sa** (الرياض) — Riyadh municipality 2024 weekly permit summaries, scraped from news archive. Currently contributes **2 rows** in `permits_historical` (2024 year-end aggregates). Modern Riyadh coverage in this dataset is essentially limited to these 2 rows.
- **REGA Annual Reports** — `rega.gov.sa/about-us/board-decisions-and-reports` — 7 PDFs (2018-2024) cached in [`pdfs/`](pdfs/).

---

## Limitations & caveats

- **48,605 `permits_raw` rows have NULL `issued_date`.** Some upstream sources publish month-bucket aggregates as individual rows without a single issued date. Treat these as month/quarter-bucket records, not point-in-time events.
- **2 rows show `2064` as the year** — almost certainly Hijri/Gregorian transcription errors in the upstream. Filter these for time-series work.
- **Riyadh has NO meaningful modern coverage in this release.** The Saudi Open Data Portal does not publish Riyadh per-permit datasets, and Riyadh's municipal authority (Riyadh City RCRC) publishes 0 permit datasets via the portal we monitor. The only Riyadh entries in this dataset are: (a) 1,022 KAPSARC historical rows ending in 2019, and (b) 2 year-end aggregate rows from `alriyadh.gov.sa` news for 2024. **There is no monthly/quarterly/per-permit Riyadh data for 2020–2026 in this release.**
- **Eastern Province coverage starts in 2025.** The Eastern Province amana was added to our pipeline late; deep historical backfill is not yet available.
- **Makkah, Jeddah, Asir, Hail, Northern Borders, Jazan, Najran, Sakaka:** zero-or-symbolic coverage. See Coverage table for specifics.
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
