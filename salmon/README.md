# Scottish salmon, sea lice and rod catch

Atlantic salmon rod catch in Scotland has fallen to the lowest levels in a series
that begins in 1952. This analysis asks how much of the west coast's steeper
decline can be associated with salmon farming, and finds that the data Scotland
publishes is not able to settle it — which turns out to be the more interesting
result.

For a plain-English summary of the findings, read the [Scottish Salmon Briefing](https://claude.ai/artifact/2FH4RHga3QieFZMPe9cmUN).

## Running it

```bash
pip install -r ../requirements.txt
python src/04_national_series.py        # any stage, from any working directory
for f in src/[0-9]*.py; do python "$f"; done   # all of them
```

Figures are written to `outputs/figures/`. The processed datasets the scripts read
are committed to this repository, so a fresh clone runs without downloading anything.

## Stages

| Script | Reads | Produces |
|---|---|---|
| `01_catch_context.py` | embedded | Rod catch context — *exploratory, superseded by 04* |
| `02_flows_and_survival.py` | embedded | Marine survival and flows — *exploratory, superseded* |
| `03_west_east_divergence.py` | embedded | West/east divergence — *exploratory, superseded by 04* |
| `04_national_series.py` | `national`, `zones` | `salmon_05_series`, `salmon_06_west_east` |
| `05_sea_trout_timing.py` | `zones`, `trout_zones` | `salmon_07_seatrout` |
| `06_farm_biomass.py` | `farms` | `salmon_08_map`, `salmon_09_biomass` |
| `07_wild_lice_vs_biomass.py` | `wildlice`, `farms` | `salmon_10_lice_biomass` |
| `08_conservation_grades.py` | embedded | `salmon_11_gradings` |
| `09_exploitation.py` | `exploit` | `salmon_12_exploitation` |
| `10_missing_counts.py` | `lice` | `salmon_13_nocount` |
| `11_timing_windows.py` | `zones` | `salmon_14_windows` |
| `12_species_specificity.py` | `wildlice`, `farms` | `salmon_15_species_specificity` |
| `13_lice_and_temperature.py` | `lice_with_temp` | `salmon_16_lice_temperature` |
| `14_robustness_checks.py` | four datasets | printed statistics, no figure |

Stages 01–03 are earlier drafts kept because they run and they show the working.
The published figures come from 04 onwards.

## The central finding

`10_missing_counts.py` is the one worth reading first. Around 17% of farm site-weeks
carry no sea lice count at all. The absence is not random: counts recorded at the
same site within three weeks of a gap sit above that site's own median, and sit
furthest above it when the stated reason for the gap is harvest withdrawal
(+0.56 adult female lice per fish, against +0.17 for counted weeks, which is what
right-skew alone would produce). Newly stocked sites run the other way, as they
should. Correcting for it lifts the national series without changing its shape.

The weeks nobody counts are the weeks with the most lice.

## Data

### `data/processed/` — committed

| Dataset | Rows × cols | Contents |
|---|---|---|
| `rod` | 56,847 × 24 | Rod catch by district, region, method, year, month |
| `exploit` | 74 × 4 | Released / retained, total, release rate |
| `national` | 74 | National annual series, 1952–2025 |
| `farms` | 79,996 × 13 | Farm production: biomass on site, mortalities, operator, grid reference |
| `lice` | 34,507 × 16 | Weekly farm lice counts, including `Reason For No Count` |
| `wildlice` | 26,068 × 7 | Wild sea trout lice counts by site, date and fish |
| `lice_with_temp` | 24,404 × 18 | Wild lice joined to daily sea temperature |
| `sst_daily` | 25,940 × 3 | Daily sea temperature by logger site |
| `zones`, `zones_idx`, `trout_zones` | 74 × 2 | Aquaculture / east-coast zone classifications |

### `data/raw/` — not committed

Source files are listed in `data/raw/README.md` with their origin. They total around
37 MB and are gitignored: they are public downloads, they do not change, and nothing
in `src/` reads them.

**This is the repository's main limitation, and it is a real one.** The step that
turns the raw downloads into the processed datasets was done interactively and was
never written down as code. The processed data is therefore the earliest point this
pipeline can reproduce from. Rebuilding that step — column selection, the zone
classification, and the nearest-logger temperature join — is the first thing I would
write if I came back to this.

## Caveats that belong with any figure from this analysis

- **Rod catch is the only long series available, and it is effort-unadjusted.**
  Angler effort was not logged until 2023. A fall in catch is not by itself a fall
  in fish.
- **Missingness in the lice data is substantial and non-random**, as above. Any lice
  figure quoted without it is biased low.
- **The temperature join uses the nearest logger site**, which is an approximation
  across a long and indented coastline.
- **Association is not dose-response.** The lice sampling coordinates that would
  allow a dose-response analysis are not published.
- Scotland's fish counters, which count ascending fish directly rather than inferring
  them from catch, run almost entirely on the east coast.

## Working scripts

The original working scripts, including the build scripts for the articles, are not published here: they carry absolute paths, will not run as-is, and contain draft article text. The figures in the published pieces come from the stages in `src/` above. The working scripts are available on request for anyone checking where a figure came from.
