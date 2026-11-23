# Source data

Not committed (see `.gitignore`). Re-exportable from Global Fishing Watch.

| Path | Size | Source |
|---|---|---|
| `gfw_iuu_insights/{2019..2025}_iuu_insights_v1_pipe4.csv` | ~20-26 MB each | Global Fishing Watch vessel insights, one row per vessel-year |
| `gfw_fishing_hours/dogger_bank_trawlers_2024.csv` | 4.6 KB | GFW fishing-hours export, trawlers, Dogger Bank polygon, 2024 |
| `gfw_fishing_hours/UNVERIFIED_area_trawlers_2019.csv` | 8.4 KB | GFW fishing-hours export, 2019 — **area not verified, see below** |
| `boundaries/dogger_bank_query_polygon.geojson` | 302 B | The polygon used for the 2024 query |

Global Fishing Watch data is licensed CC BY-SA 4.0 unless otherwise stated;
their code is Apache 2.0. Attribute accordingly.

## The 2019 file

`UNVERIFIED_area_trawlers_2019.csv` is named that way deliberately. It was
exported separately and its query polygon was not saved. Its contents do not
look like a 2019 snapshot of the same area as the 2024 file:

|  | 2019 file | 2024 file |
|---|---|---|
| Vessels | 57 | 30 |
| Total fishing hours | 3,050 | 14,463 |
| Dominant flags | Denmark 24, UK 13, Netherlands 10 | UK 28, Netherlands 1, Norway 1 |

Half the vessels but nearly five times the hours, and a complete inversion of the
flag composition. That is not a plausible before/after for one polygon. Treat the
two as unrelated until 2019 is re-exported for the polygon in
`boundaries/dogger_bank_query_polygon.geojson`.
