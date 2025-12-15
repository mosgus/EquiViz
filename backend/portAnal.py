"""
Generates portfolio analysis visuals using data in current_portfolio and stock_data.
Currently outputs a pie chart of portfolio value composition.
"""

import matplotlib

# Use non-GUI backend for server environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from pathlib import Path  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
CURRENT_PORTFOLIO_DIR = BASE_DIR / "current_portfolio"
STOCK_DATA_DIR = BASE_DIR / "stock_data"


def _latest_price(ticker: str) -> float | None:
    csv_path = STOCK_DATA_DIR / f"{ticker}.csv"
    if not csv_path.exists():
        return None
    try:
        df = pd.read_csv(csv_path, parse_dates=["Date"])
        if df.empty or "Adj Close" not in df.columns:
            return None
        return float(df["Adj Close"].iloc[-1])
    except Exception:
        return None


def _load_portfolio() -> pd.DataFrame:
    csv_files = list(CURRENT_PORTFOLIO_DIR.glob("*.csv"))
    if not csv_files:
        return pd.DataFrame()
    try:
        df = pd.read_csv(csv_files[0])
        return df
    except Exception:
        return pd.DataFrame()


def _build_value_df() -> pd.DataFrame:
    portfolio = _load_portfolio()
    if portfolio.empty or not {"Asset", "Quantity"}.issubset(portfolio.columns):
        return pd.DataFrame()

    assets = []
    for _, row in portfolio.iterrows():
        ticker = str(row["Asset"]).strip().upper()
        try:
            qty = int(row["Quantity"])
        except Exception:
            continue
        price = _latest_price(ticker)
        if price is None:
            continue
        value = price * qty
        assets.append({"Asset": ticker, "Quantity": qty, "Price": price, "Value": value})

    if not assets:
        return pd.DataFrame()

    df = pd.DataFrame(assets)
    df = df.groupby("Asset", as_index=False).agg({"Quantity": "sum", "Value": "sum"})
    return df


def _save_pie(df: pd.DataFrame) -> Path | None:
    if df.empty or df["Value"].sum() <= 0:
        return None

    CURRENT_PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CURRENT_PORTFOLIO_DIR / "PApie.png"

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(df["Value"], labels=df["Asset"], autopct="%1.1f%%", startangle=140)
    ax.set_title("Portfolio Value Composition")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def run_portfolio_analysis() -> Path | None:
    """
    Build basic analytics (currently a value pie chart) for the current portfolio.
    Returns path to the generated pie chart, or None if not created.
    """
    df = _build_value_df()
    return _save_pie(df)
