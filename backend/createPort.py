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

    # 2. Validate Ticker (Basic check)
    # TODO: Integrate with a yfinance or other API to verify ticker existence
    if not ticker or not ticker.isalpha():
        return False, "Ticker symbol must contain letters only (e.g. AAPL)."
    if len(ticker) > 5:
        return False, "Ticker symbol looks too long."

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