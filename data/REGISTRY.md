# Data Registry — Catalog of Every Dataset in This Repo

The registry is a **machine-readable index** of every CSV / CSV.GZ file in the data directories (`gastat/`, `kapsarc/`, `moj/`, `rega/`, `sama/`, `data/`). It's generated automatically by [`scripts/build_registry.py`](../scripts/build_registry.py) and published here in five CSV files plus two JSON files for programmatic use.

**Why this exists:** with 400+ data files across 5 publishers and 38 categories, just listing filenames isn't enough. You need to know which columns each file has, what values appear, which regions are covered, and how to join across sources. The registry answers all of those without you having to open every CSV.

---

## What's in `data/`

| File | Rows | Description | Format |
|---|---:|---|---|
| `registry_files.csv` | ~360 | One row per data file — source, category, path, size, row count, columns, encoding, date range, regions covered | CSV (UTF-8) |
| `registry_fields.csv` | ~2,700 | One row per column across all files — Arabic name, English name, canonical name, data type, null count, distinct count, min/max, sample values | CSV (UTF-8) |
| `registry_enums.csv` | ~8,800 | For low-cardinality columns: every distinct value + count + percentage | CSV (UTF-8) |
| `registry_samples.csv` | ~3,500 | Sample raw lines (5–10 per file) with parsed JSON — gives you a feel for each file without downloading it | CSV (UTF-8) |
| `registry_field_aliases.csv` | ~60 | Cross-source canonical name mappings (e.g. `area` ← `المساحة` across 24 MOJ files) | CSV (UTF-8) |
| `registry.json` | — | Nested view of `files` + `field_aliases` for programmatic consumers | JSON |
| `schema.json` | — | Column-by-column schema for the 5 registry CSVs | JSON |
| `region_mapping.csv` | ~50 | Canonical Saudi region names: AR ↔ EN ↔ admin code | CSV (UTF-8) |

The underlying SQLite database (`registry.db` at the repo root) is **gitignored** — power users can regenerate it locally by running `python3 scripts/build_registry.py`. The five CSVs above are the canonical published form.

---

## Schema details

### `registry_files.csv`

One row per data file in the repo. Use this to discover what's available.

| Column | Type | Notes |
|---|---|---|
| `id` | int | Surrogate key (joins to `registry_fields.file_id`) |
| `source` | text | `MOJ`, `REGA`, `GASTAT`, `SAMA`, `KAPSARC` |
| `category` | text | Bucketed category within source (e.g. `sales`, `monthly_operations`, `poa_other`) |
| `filename` | text | File name only |
| `path` | text | Path relative to repo root |
| `file_size` | int | Bytes (decompressed size for `.csv.gz`) |
| `row_count` | int | Data rows (excludes header) |
| `col_count` | int | Number of columns |
| `encoding` | text | `utf-8`, `utf-8-sig` (with BOM), etc. |
| `has_bom` | int | 0/1 — UTF-8 BOM present at start |
| `date_range_start` | text | Earliest date detected in date columns (ISO `YYYY-MM-DD` or `YYYY`) |
| `date_range_end` | text | Latest date detected |
| `region_coverage` | text | JSON array of Saudi region names (Arabic) detected in any region column |
| `notes` | text | Free-form quirks ("pivot-table export with multi-row headers", etc.) |

### `registry_fields.csv`

One row per column across all files. Foreign key `file_id` joins to `registry_files.id`.

| Column | Type | Notes |
|---|---|---|
| `id` | int | Surrogate key |
| `file_id` | int | → `registry_files.id` |
| `ordinal` | int | 0-indexed column position in source file |
| `name_ar` | text | Original Arabic header |
| `name_en` | text | English header (if present in original) |
| `canonical_name` | text | Normalized cross-source name (e.g. `area`, `city`, `transaction_count`); NULL if not yet mapped |
| `data_type` | text | `text`, `integer`, `float`, `date`, `mixed` |
| `nullable` | int | 0/1 — has any NULL values |
| `null_count` | int | Number of NULL / empty rows in this column |
| `distinct_count` | int | Number of distinct non-null values |
| `min_value` | text | Min (stringified) |
| `max_value` | text | Max (stringified) |
| `sample_values` | text | JSON array of up to 5 example values |
| `formatting_notes` | text | Quirks: `quoted_commas`, `NULL_literal`, `percentage_strings`, etc. |

### `registry_enums.csv`

For each `registry_fields` row whose distinct value count ≤ 50, this CSV lists every distinct value and its frequency. Use it to discover the vocabulary of categorical columns.

| Column | Type | Notes |
|---|---|---|
| `id` | int | Surrogate key |
| `field_id` | int | → `registry_fields.id` |
| `value` | text | The distinct value |
| `count` | int | Occurrence count |
| `percentage` | float | % of non-null rows |

### `registry_samples.csv`

5–10 sample rows per file, both as raw CSV line and parsed JSON. Gives you a quick feel for each file without downloading it.

| Column | Type | Notes |
|---|---|---|
| `id` | int | Surrogate key |
| `file_id` | int | → `registry_files.id` |
| `row_number` | int | 1-based row number in source file |
| `raw_line` | text | Original CSV line, before splitting |
| `parsed_json` | text | JSON object mapping header → cell value |

### `registry_field_aliases.csv`

Cross-source canonical mapping: shows which Arabic column names appear under each canonical name, and in how many files. Use it when joining across sources.

| Column | Type | Notes |
|---|---|---|
| `canonical_name` | text | Normalized cross-source name |
| `name_ar` | text | Arabic variant |
| `source` | text | `MOJ`, `REGA`, etc. |
| `file_count` | int | How many files in that source use this AR label |

---

## How to use the registry

### Quick start (pandas)

```python
import pandas as pd

files = pd.read_csv("data/registry_files.csv")
fields = pd.read_csv("data/registry_fields.csv")
enums = pd.read_csv("data/registry_enums.csv")

# "Which MOJ files mention area as a column?"
area_field_ids = fields[fields.canonical_name == "area"].id
files_with_area = fields[fields.id.isin(area_field_ids)].file_id.unique()
print(files[files.id.isin(files_with_area)][["filename", "row_count"]])
```

### Quick start (DuckDB — SQL across CSVs)

```sql
INSTALL spatial; -- optional, for joins
CREATE VIEW files  AS SELECT * FROM read_csv('data/registry_files.csv');
CREATE VIEW fields AS SELECT * FROM read_csv('data/registry_fields.csv');
CREATE VIEW enums  AS SELECT * FROM read_csv('data/registry_enums.csv');

-- "What values does the 'building material' column take?"
SELECT e.value, e.count, e.percentage
  FROM enums e
  JOIN fields f ON e.field_id = f.id
  WHERE f.canonical_name = 'building_material'
  ORDER BY e.count DESC;
```

### Quick start (SQLite — if you regenerate the DB locally)

```bash
python3 scripts/build_registry.py
sqlite3 registry.db
.tables
SELECT source, COUNT(*) FROM files GROUP BY source;
```

---

## How to decompress `.csv.gz` files

Some larger CSV files in this repo are gzip-compressed (`.csv.gz`) to stay under GitHub's 100 MB file-size limit. They're transparent to most modern data tools — but if you need plain CSV, here's how to decompress with free tools per platform.

### macOS

**Built-in** (no install needed):
```bash
gunzip -k data/permits/csv/permits_raw.csv.gz
# Produces permits_raw.csv next to it. -k keeps the .gz original.
```

**GUI:** [The Unarchiver](https://theunarchiver.com/) (free, Mac App Store) — double-click any `.csv.gz`.

### Windows

**Built-in (Windows 10/11):**
```powershell
tar -xzf permits_raw.csv.gz
```

**GUI:** [7-Zip](https://www.7-zip.org/) (free, open-source) — right-click `.csv.gz` → 7-Zip → Extract here.

### Linux

**Built-in:**
```bash
gunzip -k permits_raw.csv.gz
```

### Cross-platform (no decompression needed)

Most data libraries read `.csv.gz` directly without manual decompression:

```python
# pandas
import pandas as pd
df = pd.read_csv("data/permits/csv/permits_raw.csv.gz")  # auto-detects gzip
```

```python
# polars
import polars as pl
df = pl.read_csv("data/permits/csv/permits_raw.csv.gz")
```

```sql
-- DuckDB
SELECT * FROM read_csv_auto('data/permits/csv/permits_raw.csv.gz');
```

```r
# R
df <- read.csv(gzfile("data/permits/csv/permits_raw.csv.gz"))
```

---

## Rebuilding the registry

If you've added or modified data files locally and want to refresh the registry CSVs to match:

```bash
python3 scripts/build_registry.py
```

This scans every `.csv` and `.csv.gz` under the data directories, rebuilds `registry.db`, and re-exports all five CSVs and both JSON files into `data/`. Idempotent — run as often as you like; output is deterministic given the same inputs.

CI on this repo runs the same script on every push (see [`.github/workflows/registry-check.yml`](../.github/workflows/registry-check.yml)) and fails if the committed CSVs drift from what the script produces — so contributors don't accidentally publish stale catalogs.

---

## Coverage check (validation)

A separate script, [`scripts/validate_release.py`](../scripts/validate_release.py), audits the broader release state — files in wrong formats (e.g. `.xlsx` still present), large CSVs that should be compressed, data directories missing READMEs, registry CSV staleness. Run it locally:

```bash
python3 scripts/validate_release.py
```

CI also runs this on every push.

---

## See also

- [`README.md`](../README.md) — repo overview + dataset highlights
- [`CHANGELOG.md`](../CHANGELOG.md) — release-level updates
- [`GLOSSARY.md`](../GLOSSARY.md) — Saudi RE terminology
- [`LICENSE-DATA.md`](../LICENSE-DATA.md) — KSA Open Data License
- [`data/permits/README.md`](permits/README.md) — building permits dataset (largest single subset)
