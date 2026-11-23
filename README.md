# Lichen: data and analysis

Code, derived data and charts behind [Lichen](https://SUBSTACK-ADDRESS), a newsletter of data-led investigations into nature, climate and the money behind them, written by Fraser Brydon.

Every Lichen piece is built the same way: primary sources, original analysis, a plain statement of what the data can't show, and corrections published in the piece itself. This repository holds the working for each investigation so that anyone can check it, rerun it or argue with it.

## Investigations

| Folder | Investigation | What's included |
|---|---|---|
| [`salmon/`](salmon/) | Scotland's wild salmon decline, salmon farming, sea lice and rod catch, 1952–2025 | Code, processed data and figures. Runs on a fresh clone with no downloads |
| [`trawling/`](trawling/) | Did the UK's offshore marine protected areas stop bottom trawling? Event study, wild cluster bootstrap and habitat-matched synthetic controls on ICES fishing data, 2009–2025 | Code, derived results and charts. Raw ICES data must be downloaded |
| [`fisheries-effort/`](fisheries-effort/) | How much of the global fishing fleet switches off its tracking, and what one year of trawling at Dogger Bank looks like | Code, derived tables and figures. Raw Global Fishing Watch data must be downloaded |

## Headline findings

- **Salmon: the weeks nobody counts are the weeks with the most lice.** About 17% of Scottish farm site-weeks have no sea lice count, and the gaps are not random: counts just before a harvest withdrawal sit well above each site's median, so the published national series runs low.
- **Trawling: the bans cut trawling where they apply.** Trawling hours inside banned offshore sites fell by an estimated 88% relative to comparison waters (95% interval 48% to 97%). Most trawling inside protected areas happens where no ban has yet reached.
- **Fishing effort: the count and the rate disagree.** The number of fishing vessels going dark for over 24 hours rose 29% between 2019 and 2023, but as a share of the observed fleet it was flat, then fell to 1.5%.

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
