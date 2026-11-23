# Lichen: data and analysis

Code, derived data and charts behind [Lichen](https://SUBSTACK-ADDRESS), a newsletter of data-led investigations into nature, climate and the money behind them, written by Fraser Brydon.

Every Lichen piece is built the same way: primary sources, original analysis, a plain statement of what the data can't show, and corrections published in the piece itself. This repository holds the working for each investigation so that anyone can check it, rerun it or argue with it.

## Investigations

| Folder | Investigation | Status |
|---|---|---|
| [`trawling/`](trawling/) | Did the UK's offshore marine protected areas stop bottom trawling? An event study, wild cluster bootstrap and habitat-matched synthetic controls on ICES fishing data, 2009–2025. | Code, results and charts |
| `salmon/` | Scotland's wild salmon decline, the farms, and how lice are measured. | To be added |

## What is and isn't here

- **Included:** all analysis scripts, the derived tables each script produces (in each `results/` folder), and the published charts.
- **Not included:** the raw source data, which is large and belongs to its publishers. Each investigation's README lists where to download it and where to put it so the scripts run.
- **Licences:** the code is MIT-licensed. Derived data stays under its publishers' licences; see [DATA_SOURCES.md](DATA_SOURCES.md).

## Corrections

If you find an error, open an issue or reply to the newsletter. Confirmed errors are fixed here and noted in the published piece.

## Running the code

Python 3.11 or later:

```
pip install -r requirements.txt
```

Then follow the order in each investigation's README.
