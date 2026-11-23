# Bottom trawling in UK offshore marine protected areas

Working for Lichen's two-part trawling investigation (December 2026).

**Question:** when the Marine Management Organisation banned bottom-towed fishing in offshore marine protected areas (Stage 1 in 2022, Stage 2 in 2024), did trawling inside those sites actually fall, and by how much compared with what would have happened anyway?

## Data

| Source | What it gives | Put it in |
|---|---|---|
| ICES Technical Service *ospar.2026.12* (published 5 October 2026): OSPAR spatial data layers of fishing intensity, 2009–2025 | Fishing hours, swept area and landed value by 0.05° c-square, year and gear | `ices/raw/` (the OSPAR_*.shp files) |
| JNCC Offshore MPAs (December 2025 release) | Site boundaries | `bounds/jncc/` |
| MMO Marine Conservation Byelaws | Boundaries and dates of the trawling bans | `bounds/mmo/` |
| Natural England MCZ and SAC boundaries | Inshore site boundaries | `bounds/ne/` |
| Crown Estate and Crown Estate Scotland offshore wind layers | Wind farm areas, used as exclusions and in the wind comparison | `wind/raw/` |
| EMODnet Seabed Habitats, EUSeaMap 2025 (UK cut) | Broad habitat types, used to match synthetic-control donors | `data/EUSeaMap_2025_UK/` |
| Global Fishing Watch apparent fishing effort, trawlers and dredgers, 2016–2026 (only for the ICES comparison chart) | Independent satellite-based effort grids | `grids/`, loaded with `scripts/ingest.py` |
| Defra Stage 3 consultation site list | The sites proposed for the next round of bans | `bounds/stage3_sites.csv` (included) |

The ICES data are aggregated from vessel monitoring systems, which only cover vessels of 12 metres and over. **Smaller vessels are not in the data**, so inshore trawling by small boats is not measured. This is the main limit on the analysis.

## Order to run

1. `ices/ingest_ices.py`: converts each OSPAR layer and year to Parquet in `ices/store/` and writes `results/ices_inventory.csv` as a check.
2. `ices/make_csquares.py`: builds one c-square geometry layer, `ices/csquares.gpkg`.
3. `analysis/zones.py`: registry of analysis zones (existing bans, Stage 3 sites), giving `results/zones.gpkg`.
4. `analysis/build.py` and `analysis/panel2.py`: site-by-year panels of trawling inside each banned site and in distance rings around it (rings exclude all bans and wind farms).
5. `analysis/summary.py`, `event.py`, `displace.py`, `edge.py`, `resid.py`: descriptive results, the event study, displacement into surrounding waters, and checks on boundary-straddling cells.
6. `analysis/inference.py` and `wildboot.py`: PPML difference-in-differences with site-clustered errors, leave-one-site-out, randomisation inference on ban timing, and a wild cluster score bootstrap over the 15 site clusters.
7. `analysis/synth.py`, then `hab.py`, `hab_sites.py` and `synth_hab.py`: synthetic controls for each banned site, first matched on pre-ban trawling, then also on habitat (donors within an L1 distance of 0.6 on habitat shares).
8. `analysis/gap.py` and `gap2.py`: how much trawling happens inside protected sites that no ban yet covers.
9. `analysis/metrics.py`: hours, landed value, swept-area ratio and modelled benthic status by zone and year.
10. `analysis/scotland.py`, `wind.py`, `wind_event.py`, `inf_scot_wind.py`: Scottish waters and the offshore wind comparison.
11. `analysis/boulders.py`: checks around the MMO's published boulder positions at Dogger Bank.
12. Charts: `analysis/charts_v2.py`, `chart05.py`, `chart09.py`, `map.py` (house style in `lichen_style.py`). Earlier chart versions are in `analysis/archive/`.

## Main result

Estimated change in trawling hours inside banned sites, relative to comparison waters (from `results/inf_robust.csv`):

| Specification | Sites | Change | 95% interval |
|---|---|---|---|
| Main: all hours inside vs 25-50 km ring (PPML) | 15 | -88% | -97% to -48% |
| Wholly-inside cells only | 11 | -96% | -100% to -70% |
| Control ring 10-25 km | 15 | -87% | -97% to -37% |
| Control ring 50-100 km | 15 | -89% | -98% to -44% |
| Excluding Dogger Bank | 14 | -74% | -84% to -55% |
| Dropping the part-year ban year | 15 | -91% | -98% to -62% |
| Outcome: swept area, not hours | 15 | -92% | -98% to -67% |
| OLS on log(hours+1), HC1 SE (not clustered) | 15 | -83% | -88% to -75% |
| All 20 banned sites | 20 | -87% | -97% to -43% |
| With site-specific linear trends | 15 | -83% | -97% to -11% |

The intervals are wide because there are only 15 sites. Dogger Bank is the largest single influence: without it the estimate is −74%. The synthetic-control results are in `results/synth.csv` and `results/synth_hab.csv`.

## Known limits

- Vessels under 12 metres are not covered by the ICES data.
- Effort is aggregated to 0.05° c-squares, so cells that straddle a boundary are split by area (`edge.py` tests how much this matters).
- Two vessels seen at Dogger Bank are thought to be guard vessels for offshore infrastructure rather than fishing boats; this could not be confirmed, so they are flagged rather than reclassified.
