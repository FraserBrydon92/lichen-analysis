"""
Shared paths, data loading and plotting setup for the salmon / sea lice analysis.

Every stage script imports from here, so nothing in src/ contains an absolute
path. Paths resolve from this file's own location, which means the scripts run
correctly from any working directory after a fresh clone.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data" / "processed"
RAW = PROJECT / "data" / "raw"
FIGS = PROJECT / "outputs" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

# Columns that must come back as dates after a CSV round trip. The original
# analysis held these datasets as pickles, where dtypes survived; CSV does not
# carry them, so they are parsed explicitly here rather than left as strings.
DATE_COLUMNS = {"date", "Week Beginning"}

# Datasets whose first CSV column is the index, not a variable.
INDEXED = {"national", "zones", "zones_idx", "trout_zones", "exploit"}


def load(name: str) -> pd.DataFrame:
    """Load a processed dataset by name, without the .csv extension."""
    path = DATA / f"{name}.csv"
    if not path.exists():
        raise SystemExit(
            f"Missing {path}.\n"
            f"The processed datasets are committed to this repository; see "
            f"{PROJECT / 'README.md'} if this file is absent."
        )
    df = pd.read_csv(path, index_col=0 if name in INDEXED else None, low_memory=False)
    for col in df.columns:
        if col in DATE_COLUMNS:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def load_series(name: str) -> pd.Series:
    """Load a single-column dataset as a Series (national annual catch)."""
    df = load(name)
    return df.iloc[:, 0]


def use_font(preferred: str, fallback: str = "DejaVu Sans") -> str:
    """
    Return `preferred` if it is installed, otherwise `fallback`.

    The original charts specify Inter and Caladea. Neither ships with
    matplotlib, so on a machine without them matplotlib emits a warning per
    text object and silently substitutes. Resolving it here keeps the figures
    legible on a fresh clone instead of failing noisily.
    """
    available = {f.name for f in font_manager.fontManager.ttflist}
    return preferred if preferred in available else fallback


def save(fig, name: str, dpi: int = 200) -> None:
    """Write a figure into outputs/figures and close it."""
    out = FIGS / name
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    print(f"wrote {out.relative_to(PROJECT)}")
