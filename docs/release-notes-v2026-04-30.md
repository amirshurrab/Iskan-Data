# Release Notes — v2026-04-30 (Patch)

**Type:** Data correction
**Affects:** `rega/bulletins/rega_bulletin_timeseries.csv` only
**No new PDFs added.**

## Summary

Corrects mis-labeled rows in the January 2026 portion of the bulletin
timeseries shipped in `v2026-04-28`. The parser used to generate the
CSV assumed every monthly bulletin laid sections out in the same page
order. REGA reordered pages between the January and February 2026
issues, which silently rotated the January numbers by one section.

## What changed in January 2026 rows

- **Rental rows** (residential + non-residential, contract_count /
  transaction_count / transaction_value): values previously shown were
  taken from the residential breakdown section, not the rental table.
- **Residential breakdown — counts and values**: the cells published
  here in `v2026-04-28` were actually the average-area and
  average-transaction-value figures.
- **Residential breakdown — average area**: the cells published here
  were actually rental figures.
- **Residential breakdown — average transaction value**: was missing
  entirely (zero rows). Now populated for all six sub-types.

In short: 30 of 38 January 2026 rows had the right value but the
wrong label, plus 6 rows were missing. After this release they all
carry the correct label and value pulled from the matching section of
the source PDF.

## What did NOT change

- Sales section for January 2026 — was correct in `v2026-04-28` and
  remains identical.
- All February and March 2026 rows — were correct in `v2026-04-28`
  and remain identical.
- The five source PDFs — unchanged. The correction is in the parser's
  page-to-section mapping; the underlying PDFs are authoritative and
  were always right.

## Verification

The corrected values pass plausibility checks across the three months
shipped:

- `avg_area` for `apartment` is 163 m² in all three months (stable
  household-size proxy).
- `avg_area` for `land` lands at 561 / 553 / 554 m² (stable
  residential-plot proxy).
- Residential rental `transaction_value` lands in the multi-billion
  SAR range each month, consistent with national-scale figures.
- Residential rental `contract_count` ranges 180K–280K per month,
  consistent with the order of magnitude REGA reports for the rental
  market nationally.

## Row count

- `v2026-04-28`: 107 data rows
- `v2026-04-30`: 113 data rows (+6, all in January 2026
  `avg_txn_value` for the six residential sub-types)

## Schema

Unchanged. Same 14 columns as `v2026-04-28`:

```
month, publication_date, section, indicator, segment, sub_type,
region, region_rank, metric, value, unit, mom_pct, yoy_pct, source_pdf
```

## How to upgrade

If you depend on the timeseries CSV, re-pull the file. No schema
migration required.

```bash
curl -O https://raw.githubusercontent.com/civillizard/Saudi-Real-Estate-Data/main/rega/bulletins/rega_bulletin_timeseries.csv
```

If you have already loaded the CSV into a downstream system, refresh
the January 2026 rows (months `2026-01`); February and March 2026 are
identical to before so do not need re-loading.

## Acknowledgements

This correction was caught by an internal parser audit that compared
the v1 output against header text on each page of each bulletin PDF.
The next bulletin parser pass will dispatch by Arabic header text on
every page rather than by hardcoded page number, so future REGA page
reorderings won't silently rotate the data.
