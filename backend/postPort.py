import yfinance as yf
from datetime import datetime


def validate_portfolio_input(data):
    """
    Checks if portfolio inputs are possible/correct.
    Returns: (is_valid, message)
    """
    name = data.get('name')
    ticker = data.get('ticker')
    quantity = data.get('quantity')
    date_str = data.get('date')

    # 1. Validate Name
    if not name or len(name.strip()) == 0:
        return False, "Portfolio name cannot be empty."

    # 2. Validate Ticker
    # Basic syntax check
    if not ticker:
        return False, "Ticker symbol is required."

    # We allow the API to do the heavy verification, but we check length first
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

    # 3. Validate Quantity
    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "Quantity must be a positive number."
    except ValueError:
        return False, "Quantity must be a valid number."

    # 4. Validate Date (Cannot be in the future)
    try:
        input_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if input_date > datetime.now().date():
            return False, "Purchase date cannot be in the future."
    except ValueError:
        return False, "Invalid date format."

    # If all pass
    return True, "Portfolio created successfully!"