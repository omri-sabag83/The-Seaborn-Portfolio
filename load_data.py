"""load_data.py — fetch and cache the two Kaggle datasets used in this project.

Most examples use Seaborn's built-in datasets and just call
``sns.load_dataset("penguins")`` etc. directly in the notebook — those need
nothing from this file.

Two examples use larger, real-world data from Kaggle instead:

    load_data("california_housing")   # camnugent/california-housing-prices
    load_data("sp500")                # camnugent/sandp500  (S&P 500 daily prices)

First call:  downloads the dataset with kagglehub, applies a light cleaning pass
             (types only, no rows dropped), and writes a Parquet file under
             ``data/``.
Later calls: read that Parquet file — fast and offline.

First download needs Kaggle API credentials (one-time):
    ~/.kaggle/kaggle.json  with your API token,
    or the  KAGGLE_USERNAME / KAGGLE_KEY  environment variables.
See the README for how to create the token.

Usage inside a notebook (run from the repo root):

    from load_data import load_data
    housing = load_data("california_housing")
"""

from pathlib import Path

import pandas as pd

_REPO_DIR = Path(__file__).resolve().parent
_CACHE_DIR = _REPO_DIR / "data"

# name -> (kaggle dataset slug, preferred file inside the download)
_DATASETS = {
    "california_housing": ("camnugent/california-housing-prices", "housing.csv"),
    "sp500": ("camnugent/sandp500", "all_stocks_5yr.csv"),
}


def _clean(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Per-dataset light cleaning — column types and names only."""
    if name == "sp500":
        df["date"] = pd.to_datetime(df["date"])
        df = df.rename(columns={"Name": "ticker"})
    # california_housing arrives fully typed; nothing to do.
    return df


def load_data(name: str, refresh: bool = False) -> pd.DataFrame:
    """Return one of the Kaggle datasets as a cleaned DataFrame.

    Parameters
    ----------
    name : {"california_housing", "sp500"}
    refresh : bool, default False
        If True, ignore the cache, re-download, and rewrite it.
    """
    if name not in _DATASETS:
        raise KeyError(f"unknown dataset {name!r}; choose from {sorted(_DATASETS)}")

    cache_path = _CACHE_DIR / f"{name}.parquet"
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    slug, preferred_file = _DATASETS[name]

    try:
        import kagglehub
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "kagglehub is needed for the first download — "
            "run `pip install -r requirements.txt` in the seaborn_portfolio env"
        ) from exc

    print(f"Downloading '{slug}' from Kaggle (first run only)...")
    download_dir = Path(kagglehub.dataset_download(slug))

    csv_path = download_dir / preferred_file
    if not csv_path.exists():
        candidates = sorted(download_dir.rglob("*.csv"))
        if not candidates:
            raise FileNotFoundError(f"no CSV found in the download at {download_dir}")
        csv_path = candidates[0]

    df = _clean(name, pd.read_csv(csv_path))

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path, index=False)
    print(f"Cached to {cache_path.relative_to(_REPO_DIR)}  ({len(df):,} rows)")

    return df
