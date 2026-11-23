# Fishing effort and vessel monitoring

Two analyses built on Global Fishing Watch AIS data. Both are about the same
underlying problem: fisheries oversight depends on vessels reporting their own
positions, and the gaps in that reporting are data in their own right.

## Running it

```bash
pip install -r ../requirements.txt
python src/01_ais_disabling.py
python src/02_dogger_bank_2024.py
```

Raw data is not committed. See `data/raw/README.md` for what to download.

## `01_ais_disabling.py` — the count and the rate disagree

Of the fishing vessels Global Fishing Watch observed each year, what share had at
least one AIS disabling event longer than 24 hours?

| Year | Fishing vessels observed | Vessels disabling >24h | Rate |
|---|---|---|---|
| 2019 | 118,073 | 2,577 | 2.18% |
| 2020 | 124,834 | 2,836 | 2.27% |
| 2021 | 134,809 | 2,935 | 2.18% |
| 2022 | 143,307 | 3,069 | 2.14% |
| 2023 | 155,075 | 3,333 | 2.15% |
| 2024 | 157,557 | 2,852 | 1.81% |
| 2025 | 157,674 | 2,399 | 1.52% |

The count of vessels disabling rose by 29% between 2019 and 2023, then fell. The
rate did neither: it sat flat at roughly 2.2% for five years, then dropped to 1.5%.
The monitored fleet grew by a third over the period, and that growth is doing the
work in the count. Reporting the count alone would describe a rise that is mostly
a denominator.

Limitations are in the script, not only in this README. The important one: disabling
is inferred from gaps in transmission, so it cannot be separated from transponder
faults or poor satellite reception. A second: coverage improved over the period, so
a falling rate is partly a story about who is now being watched.

## `02_dogger_bank_2024.py` — composition inside one polygon

Apparent trawler effort inside the Dogger Bank query polygon in 2024: 30 vessels,
14,463 apparent fishing hours, of which UK-flagged vessels account for essentially
all. Five vessels account for 72% of the hours.

This is a description of one year in one polygon. It is **not** an assessment of the
bottom-trawling closure. The 2019 export that would make it a before/after cannot be
shown to cover the same area — 57 vessels and 3,050 hours, dominated by Danish and
Dutch flags, against 30 vessels and 14,463 hours dominated by UK flags. Half the
vessels and five times the hours is not a plausible one-polygon time series.

The comparison is maybe twenty lines of code. It is not written, because the input
to it does not exist yet. Re-exporting 2019 against the committed polygon would
close it.
