"""
AIS disabling among the world's fishing fleet, 2019-2025.

Question
--------
Vessel monitoring depends on vessels reporting their own positions. A vessel can
switch its AIS transponder off. Global Fishing Watch flags these as "disabling"
events. The headline number usually quoted is a count of vessels that disabled.
But the monitored fleet grew by roughly a third over this period, so a rising
count can simply mean a bigger fleet.

This script asks the question as a rate: of the fishing vessels observed in a
given year, what share had at least one AIS disabling event longer than 12 and
longer than 24 hours?

Inputs
------
data/raw/gfw_iuu_insights/{year}_iuu_insights_v1_pipe4.csv
One row per vessel-year. See data/README.md for provenance and licence.

Outputs
-------
data/derived/ais_disabling_by_year.csv
outputs/figures/ais_disabling_rate.png

Known limitations are listed at the bottom of this file and in the README.
They are not incidental; the rate is only meaningful if you accept them.
"""

from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "gfw_iuu_insights"
DERIVED = ROOT / "data" / "derived"
FIGS = ROOT / "outputs" / "figures"

# Columns we actually use, so a schema change elsewhere in the file is harmless.
COLS = [
    "mmsi", "year", "vessel_class", "is_fishing", "best_flag",
    "hours", "active_hours", "gaps_count",
    "disabling_over_12_hours", "disabling_over_24_hours",
    "iuu_listed", "previously_iuu_listed",
]


def load_year(path: Path) -> pd.DataFrame:
    """Read one vessel-year file, keeping only fishing vessels."""
    df = pd.read_csv(path, usecols=COLS, low_memory=False)

    # is_fishing arrives as a real bool in some years and as a string in others.
    is_fishing = df["is_fishing"].astype(str).str.lower().isin(["true", "1"])
    df = df.loc[is_fishing].copy()

    # A missing disabling count means "none recorded", not "unknown": GFW emits
    # the field for every vessel it assessed. Treating it as 0 is a choice, and
    # it is the conservative one for a rate (it can only lower the numerator).
    for col in ["disabling_over_12_hours", "disabling_over_24_hours", "gaps_count"]:
        df[col] = df[col].fillna(0)

    return df


def main() -> None:
    files = sorted(RAW.glob("*_iuu_insights_v1_pipe4.csv"))
    if not files:
        raise SystemExit(f"No input files found in {RAW}. See data/README.md.")

    records = []
    for path in files:
        year = int(path.name[:4])
        df = load_year(path)

        # Each file should contain exactly one year. Assert rather than assume,
        # because a mixed file would silently distort every rate below.
        years_present = sorted(df["year"].dropna().unique().tolist())
        assert years_present == [year], f"{path.name} contains years {years_present}"

        vessels = len(df)
        records.append({
            "year": year,
            "fishing_vessels_observed": vessels,
            "vessels_disabling_over_12h": int((df["disabling_over_12_hours"] > 0).sum()),
            "vessels_disabling_over_24h": int((df["disabling_over_24_hours"] > 0).sum()),
            "total_disabling_events_over_12h": int(df["disabling_over_12_hours"].sum()),
            "total_disabling_events_over_24h": int(df["disabling_over_24_hours"].sum()),
            "total_ais_gaps": int(df["gaps_count"].sum()),
            "vessels_iuu_listed": int(df["iuu_listed"].astype(str).str.lower().isin(["true", "1"]).sum()),
        })

    out = pd.DataFrame(records).sort_values("year").reset_index(drop=True)

    # The point of the script: counts normalised by the fleet actually observed.
    out["pct_disabling_over_12h"] = (
        100 * out["vessels_disabling_over_12h"] / out["fishing_vessels_observed"]
    ).round(2)
    out["pct_disabling_over_24h"] = (
        100 * out["vessels_disabling_over_24h"] / out["fishing_vessels_observed"]
    ).round(2)

    DERIVED.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    out.to_csv(DERIVED / "ais_disabling_by_year.csv", index=False)

    print(out.to_string(index=False))
    print()
    first, last = out.iloc[0], out.iloc[-1]
    print(
        f"Vessels with a >24h disabling event: "
        f"{int(first.vessels_disabling_over_24h):,} of {int(first.fishing_vessels_observed):,} "
        f"({first.pct_disabling_over_24h}%) in {int(first.year)}, "
        f"{int(last.vessels_disabling_over_24h):,} of {int(last.fishing_vessels_observed):,} "
        f"({last.pct_disabling_over_24h}%) in {int(last.year)}."
    )

    # ---- figure ----------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))

    ax1.bar(out["year"], out["vessels_disabling_over_24h"], color="#8c8c8c")
    ax1.set_title("Count: vessels with a >24h\nAIS disabling event", fontsize=11)
    ax1.set_ylabel("Vessels")

    ax2.plot(out["year"], out["pct_disabling_over_24h"], marker="o", color="#1a1a1a", label=">24 hours")
    ax2.plot(out["year"], out["pct_disabling_over_12h"], marker="o", color="#9a9a9a", label=">12 hours")
    ax2.set_title("Rate: share of observed fishing\nvessels that disabled", fontsize=11)
    ax2.set_ylabel("% of fishing vessels observed")
    ax2.set_ylim(0, max(out["pct_disabling_over_12h"]) * 1.25)
    ax2.legend(frameon=False, fontsize=9)

    for ax in (ax1, ax2):
        ax.set_xlabel("Year")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)

    fig.suptitle(
        "The count and the rate tell different stories (Global Fishing Watch, 2019-2025)",
        fontsize=12, y=1.02,
    )
    fig.text(
        0.0, -0.06,
        "Denominator is fishing vessels observed by GFW in that year, which grew from "
        f"{out.fishing_vessels_observed.iloc[0]:,} to {out.fishing_vessels_observed.iloc[-1]:,}.\n"
        "Disabling is inferred from AIS gaps, so it cannot distinguish a deliberate switch-off from "
        "a technical fault or loss of satellite reception.",
        fontsize=8, color="#555555", va="top",
    )
    fig.tight_layout()
    fig.savefig(FIGS / "ais_disabling_rate.png", dpi=200, bbox_inches="tight")
    print(f"\nWrote {DERIVED / 'ais_disabling_by_year.csv'}")
    print(f"Wrote {FIGS / 'ais_disabling_rate.png'}")


if __name__ == "__main__":
    main()


# Limitations
# -----------
# 1. Disabling is inferred, not observed. GFW identifies it from gaps in AIS
#    transmission. A gap can also be a transponder fault, poor satellite
#    reception, or an area of high AIS traffic where messages collide. The
#    dataset cannot separate these from a deliberate switch-off.
# 2. The denominator is vessels GFW observed, not the world fleet. Coverage
#    improved over the period, which means later years include vessels that
#    earlier years would have missed. A falling rate is therefore partly a
#    story about who is now being watched.
# 3. total_ais_gaps rises far faster than disabling events over the same period
#    (roughly 8.2m to 19.0m). That is a coverage and traffic artefact and should
#    not be read as behaviour. It is reported here only so the contrast with the
#    disabling series is visible.
# 4. One row per vessel-year means a vessel active in several years is counted
#    once per year. These are annual cross-sections, not a tracked cohort.
