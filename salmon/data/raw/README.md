# Source data

Not committed (see `.gitignore`). Nothing in `src/` reads these files — the
pipeline starts from `data/processed/`. They are listed here so the provenance
of the processed data is on the record.

| File | Size | Source |
|---|---|---|
| `ms_sea_lice_archive.csv` | 4.8 MB | Weekly farm sea lice counts archive, Scottish Government / Marine Directorate |
| `se_monthly_reports.csv` | 20.5 MB | Monthly site-level farm reports |
| `Sea_trout_lice_counts_1997-2024_Long_ID.csv` | 5.4 MB | Wild sea trout lice counts, 1997-2024 |
| `SalmonAndSeaTroutRodCatchByStockAssessmentAreaAndMonth1952-2025.csv` | 0.6 MB | Rod catch by stock assessment area and month |
| `Salmon_and_sea_trout_rods_by_District_and_month_1952_to_2025.xlsx` | 6.2 MB | Rod catch by district and month |
| `scottish-fish-farm-production-survey-2025-supplementary-tables.xlsx` | 0.3 MB | Scottish fish farm production survey 2025, supplementary tables |
| SCOBS logger files (4) | ~28 MB each | Full-resolution 2021 sea temperature: Loch Ewe, Loch Maddy, Mallaig, Millport |

All are Scottish Government / Marine Directorate open data. Confirm the current
licence and required citation on each publication page before republishing.

The SCOBS logger files are the raw input to `sst_daily`, which is committed in
processed form.
