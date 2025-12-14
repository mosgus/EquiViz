from datetime import datetime
import csv
import re
from pathlib import Path

import yfinance as yf


def validate_portfolio_input(data):
    """
    Checks if current_portfolio inputs are possible/correct.
    Returns: (is_valid, message)
    """
    name = data.get('name')
    ticker = data.get('ticker')
    quantity = data.get('quantity')
    date_str = data.get('date')

    # Validate Name
    if not name or len(name.strip()) == 0:
        return False, "Portfolio name cannot be empty."

    # Validate Ticker
    # syntax check
    if not ticker:
        return False, "Ticker symbol is required."

    # length, not girth
    if len(ticker) > 8:
        return False, "Ticker symbol looks too long."

    # Yahoo Finance API Check
    try:
        stock = yf.Ticker(ticker)
        # fetch 5 days of history to see if data exists
        hist = stock.history(period="5d")

        if len(hist) == 0:
            return False, f"Ticker '{ticker}' could not be found on the market."

    except Exception as e:
        # In case of connection errors or API issues
        return False, f"Could not verify ticker: {str(e)}"

    # Validate Quantity
    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "Quantity must be a positive number."
    except ValueError:
        return False, "Quantity must be a valid number."

    # Validate Date (Cannot be in the future)
    try:
        input_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if input_date > datetime.now().date():
            return False, "Purchase date cannot be in the future."
    except ValueError:
        return False, "Invalid date format."

    # If all pass
    return True, "Portfolio created successfully!"

# It case tards put spaced in their names
def _slugify_name(name: str) -> str:
    safe_name = re.sub(r'[^A-Za-z0-9._-]+', '_', name).strip('_')
    return safe_name


def _clear_portfolio_dir(portfolio_dir: Path) -> None:
    if not portfolio_dir.exists():
        return
    for item in portfolio_dir.iterdir():
        if item.is_file():
            item.unlink()


def save_portfolio(data):
    """
    Append a validated current_portfolio tranche to backend/current_portfolio/<name>.csv.
    """
    name = (data.get('name') or "").strip()
    ticker = data.get('ticker')
    quantity = int(data.get('quantity'))
    date_str = data.get('date')

    # Slugify the filename to keep it filesystem-friendly
    safe_name = _slugify_name(name)
    if not safe_name:
        raise ValueError("Invalid current_portfolio name.")

    base_dir = Path(__file__).resolve().parent
    portfolio_dir = base_dir / "current_portfolio"
    saved_dir = base_dir / "saved_portfolios"
    portfolio_dir.mkdir(parents=True, exist_ok=True)

    # Block creation if a saved current_portfolio with the same name already exists
    saved_conflict = saved_dir / f"{safe_name}.csv"
    if saved_conflict.exists():
        raise ValueError("A saved current_portfolio with this name already exists. Choose a different name.")

    # Clear temp current_portfolio directory before writing a new file
    _clear_portfolio_dir(portfolio_dir)

    file_path = portfolio_dir / f"{safe_name}.csv"
    write_header = not file_path.exists()

    with file_path.open("a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["Asset", "Quantity", "Date Acquired"])
        writer.writerow([ticker, quantity, date_str])

    return file_path
