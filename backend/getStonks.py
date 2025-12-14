from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List

import pandas as pd
import yfinance as yf

BASE_DIR = Path(__file__).resolve().parent
CURRENT_PORTFOLIO_DIR = BASE_DIR / "current_portfolio"
STOCK_DATA_DIR = BASE_DIR / "stock_data"

# Used YF.py from DataGrabber

def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    cols = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    keep = [c for c in cols if c in df.columns]
    return df[keep]


def _read_existing(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, parse_dates=["Date"])
        if df.empty:
            return pd.DataFrame()
        df = df.sort_values("Date").reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()


def _fetch(symbol: str, start: str, end_exclusive: str) -> pd.DataFrame:
    return yf.download(symbol, start=start, end=end_exclusive, auto_adjust=False, progress=False)


def _update_symbol(symbol: str, start_date: datetime.date, end_date: datetime.date) -> bool:
    STOCK_DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = STOCK_DATA_DIR / f"{symbol}.csv"

    existing = _read_existing(csv_path)
    frames = []
    if not existing.empty:
        frames.append(existing)

    target_start = start_date
    target_end = end_date
    end_excl_str = (target_end + timedelta(days=1)).strftime("%Y-%m-%d")

    if existing.empty or "Date" not in existing:
        fetched = _normalize_df(_fetch(symbol, target_start.strftime("%Y-%m-%d"), end_excl_str))
        if fetched.empty:
            return False
        frames.append(fetched)
    else:
        current_start = existing["Date"].min().date()
        current_end = existing["Date"].max().date()

        if target_start < current_start:
            prepend_end_excl = current_start.strftime("%Y-%m-%d")
            fetched = _normalize_df(_fetch(symbol, target_start.strftime("%Y-%m-%d"), prepend_end_excl))
            if not fetched.empty:
                frames.append(fetched)

        if target_end > current_end:
            append_start = (current_end + timedelta(days=1)).strftime("%Y-%m-%d")
            fetched = _normalize_df(_fetch(symbol, append_start, end_excl_str))
            if not fetched.empty:
                frames.append(fetched)

        if len(frames) == 1:
            # Existing file already covers requested range
            return True

    if not frames:
        return False

    combined = pd.concat(frames, ignore_index=True)
    if "Date" in combined.columns:
        combined["Date"] = pd.to_datetime(combined["Date"])
        combined = combined.sort_values("Date").drop_duplicates(subset=["Date"], keep="last")

    combined.to_csv(csv_path, index=False, float_format="%.10f")
    return True


def _extract_tickers() -> List[str]:
    csv_files = list(CURRENT_PORTFOLIO_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No current portfolio found.")
    df = pd.read_csv(csv_files[0])
    if "Asset" not in df.columns:
        raise ValueError("Portfolio is missing required 'Asset' column.")
    tickers = (
        df["Asset"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
        .tolist()
    )
    tickers = [t for t in tickers if t]
    if not tickers:
        raise ValueError("No tickers found in portfolio.")
    return tickers


def update_current_portfolio_data(years: int = 5) -> List[str]:
    tickers = _extract_tickers()
    end_date = datetime.utcnow().date()
    # Anchor to Jan 1 of (current_year - years) so the first row aligns with the first trading day of that January.
    start_year = end_date.year - years
    start_date = date(start_year, 1, 1)

    failures = []
    for symbol in tickers:
        ok = _update_symbol(symbol, start_date, end_date)
        if not ok:
            failures.append(symbol)

    if failures:
        raise RuntimeError(f"Failed to update data for: {', '.join(failures)}")

    return tickers
