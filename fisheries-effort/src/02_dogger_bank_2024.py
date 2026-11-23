"""
Trawler fishing effort inside the Dogger Bank query polygon, 2024.

What this does and does not do
------------------------------
This describes the composition of apparent trawler effort inside one polygon in
one year. It is NOT a before/after assessment of the bottom-trawling closure,
because the 2019 export sitting alongside it cannot be shown to cover the same
area — see data/raw/README.md for the numbers that rule it out.

Writing the comparison would take about twenty lines. It is deliberately not
written, because the input to it does not exist yet.

Inputs : data/raw/gfw_fishing_hours/dogger_bank_trawlers_2024.csv
         data/raw/boundaries/dogger_bank_query_polygon.geojson
Outputs: data/derived/dogger_bank_2024_by_flag.csv
         outputs/figures/dogger_bank_2024_effort.png
"""

import json
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
FIGS = ROOT / "outputs" / "figures"

HOURS = "Total fishing hours"


def main() -> None:
    path = RAW / "gfw_fishing_hours" / "dogger_bank_trawlers_2024.csv"
    if not path.exists():
        raise SystemExit(f"Missing {path}. See data/raw/README.md to re-export it.")

    df = pd.read_csv(path)

    # Report the polygon the query used, so the geographic claim is auditable
    # rather than assumed from the filename.
    poly = json.loads((RAW / "boundaries" / "dogger_bank_query_polygon.geojson").read_text())
    coords = poly["features"][0]["geometry"]["coordinates"][0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    print(
        f"Query polygon: {len(coords) - 1} vertices, "
        f"lon {min(lons):.3f} to {max(lons):.3f}, lat {min(lats):.3f} to {max(lats):.3f}"
    )
    print(f"Vessels: {len(df)}   Total apparent fishing hours: {df[HOURS].sum():,.0f}\n")

    by_flag = (
        df.groupby("flag translated")
          .agg(vessels=("MMSI", "nunique"), fishing_hours=(HOURS, "sum"))
          .sort_values("fishing_hours", ascending=False)
    )
    by_flag["pct_of_hours"] = (100 * by_flag.fishing_hours / by_flag.fishing_hours.sum()).round(1)
    by_flag["fishing_hours"] = by_flag.fishing_hours.round(1)

    by_gear = df.groupby("GFW gear type")[HOURS].agg(["size", "sum"]).round(1)

    print(by_flag.to_string())
    print()
    print(by_gear.to_string())

    # Effort is heavily concentrated, so say by how much rather than implying
    # that 30 vessels each account for a thirtieth of it.
    top = df.nlargest(5, HOURS)
    share = 100 * top[HOURS].sum() / df[HOURS].sum()
    print(f"\nTop 5 vessels account for {share:.1f}% of all apparent fishing hours.")

    DERIVED.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    by_flag.to_csv(DERIVED / "dogger_bank_2024_by_flag.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    ax1.barh(by_flag.index[::-1], by_flag.fishing_hours[::-1], color="#2a5d78")
    ax1.set_xlabel("Apparent fishing hours")
    ax1.set_title("Effort by flag state", fontsize=11, loc="left")

    ranked = df.sort_values(HOURS, ascending=False)[HOURS].to_numpy()
    cumulative = 100 * ranked.cumsum() / ranked.sum()
    ax2.plot(range(1, len(cumulative) + 1), cumulative, marker="o", ms=4, color="#1a1a1a")
    ax2.axhline(80, color="#bb4430", linestyle=(0, (4, 3)), linewidth=1.2)
    ax2.text(len(cumulative), 81, "80% of hours", ha="right", fontsize=9, color="#bb4430")
    ax2.set_xlabel("Vessels, ranked by hours")
    ax2.set_ylabel("Cumulative % of hours")
    ax2.set_title("Effort is concentrated in few vessels", fontsize=11, loc="left")
    ax2.set_ylim(0, 105)

    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="x" if ax is ax1 else "y", alpha=0.25)

    fig.suptitle(
        "Apparent trawler effort inside the Dogger Bank query polygon, 2024",
        fontsize=12, y=1.03,
    )
    fig.text(
        0.0, -0.08,
        "Global Fishing Watch AIS-derived apparent fishing effort. Apparent effort is inferred from vessel\n"
        "movement, not observed, and AIS coverage is not complete. Single year, single polygon: this is a\n"
        "description of composition, not an assessment of the closure.",
        fontsize=8, color="#555555", va="top",
    )
    fig.tight_layout()
    fig.savefig(FIGS / "dogger_bank_2024_effort.png", dpi=200, bbox_inches="tight")
    print(f"\nWrote {DERIVED / 'dogger_bank_2024_by_flag.csv'}")
    print(f"Wrote {FIGS / 'dogger_bank_2024_effort.png'}")


if __name__ == "__main__":
    main()
