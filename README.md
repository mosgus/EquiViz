# EquiViz 📊
A Python-based equity portfolio visualizer using HTML & JS.

### Features
- **Web Interface**:
    - Run EquiViz locally via Flask and interact through the browser.
    - Create a portfolio from the UI or upload/select a CSV (`Asset, Quantity, Date Acquired`).
    - Portfolio table is enriched with $/Share, $/Share tdy, Cost, Value, Return, Return % plus a Net Total row (computed from cached data).
    - Edit portfolio via modal (CSV textarea) with validation.
    - Download the current portfolio CSV at any time.
    - Analysis page displays a value-composition pie chart generated from the current portfolio.
    - Tabs link between Portfolio, Analysis, Optimization, Sentiment, Forecasts, and Global View pages (placeholders for now).

- **Data Fetching & Caching**:
    - After any portfolio change (create/upload/select/edit), stock data is fetched/updated via yfinance into `backend/stock_data/<TICKER>.csv` (5-year history).
    - Portfolio analysis (`backend/portAnal.py`) generates `PApie.png` in `backend/current_portfolio` using the latest prices from `stock_data`.
    - Displayed metrics and charts use the cached data; the stored CSV format is unchanged.
          
### Dependencies
```bash
pip install yfinance --upgrade --no-cache-dir 
```
```bash
pip install flask
```
```bash
pip install pandas matplotlib
```

### How to run
Currently we run EquiViz locally using Flask. It will be hosted later.
```bash
python app.py
```
And then use the local server link provided.
