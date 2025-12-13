import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

from datetime import datetime
from sklearn.preprocessing import StandardScaler


# ---------- CONFIG ---------- #
STOCK_FOLDER = "STOCK DATA"


# ---------- FUNCTIONS ---------- #
def load_stock_data(ticker):
    filepath = os.path.join(STOCK_FOLDER, f"{ticker}_5yr_history.csv")
    df = pd.read_csv(filepath, parse_dates=['date'])
    df = df.drop_duplicates(subset='date')         # remove duplicate dates
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    df = df.asfreq('B')                             # ensure business-day frequency
    return df

def compute_features(df):
    df['return'] = df['prc'].pct_change()
    df['volatility_20d'] = df['return'].rolling(20).std() * np.sqrt(20)
    return df.dropna()

def forecast_price(df):
    model = sm.tsa.ARIMA(df['prc'], order=(1, 1, 1))
    results = model.fit()
    forecast = results.forecast(steps=1)
    return forecast.iloc[0], results

def detect_risk(df):
    threshold = df['volatility_20d'].quantile(0.90)
    df['high_risk'] = (df['volatility_20d'] > threshold).astype(int)
    return df, threshold

def detect_anomalies(df):
    ret_mean = df['return'].mean()
    ret_std = df['return'].std()
    df['return_anomaly'] = ((df['return'] - ret_mean).abs() > 3 * ret_std)
    vol_threshold = df['vol'].quantile(0.99)
    df['volume_anomaly'] = df['vol'] > vol_threshold
    return df

def visualize_stock(df, ticker, forecast_value, vol_thresh):
    plt.figure(figsize=(15, 8))

    plt.subplot(3, 1, 1)
    plt.plot(df.index, df['prc'], label='Price')
    plt.title(f'{ticker} Price with Forecast')
    plt.axhline(forecast_value, color='green', linestyle='--', label=f'Forecast: {forecast_value:.2f}')
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(df.index, df['volatility_20d'], label='20d Volatility')
    plt.axhline(vol_thresh, color='red', linestyle='--', label='Risk Threshold')
    plt.title('Volatility and Risk Regimes')
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(df.index, df['return'], label='Returns')
    plt.scatter(df[df['return_anomaly']].index, df[df['return_anomaly']]['return'], color='red', label='Return Anomaly')
    plt.scatter(df[df['volume_anomaly']].index, df[df['volume_anomaly']]['return'], color='orange', label='Volume Anomaly')
    plt.title('Anomaly Detection')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"output_{ticker}.png")
    plt.show()


# ---------- RUN FOR ONE STOCK ---------- #
if __name__ == '__main__':
    ticker = 'AAPL'  # change to any of your 13 stocks
    df = load_stock_data(ticker)
    df = compute_features(df)

    forecast_val, arima_model = forecast_price(df)
    df, risk_thresh = detect_risk(df)
    df = detect_anomalies(df)

    print(f"Forecasted Next Close for {ticker}: {forecast_val:.2f}")
    print(f"Current Volatility: {df['volatility_20d'].iloc[-1]:.2%}")
    print(f"Risk Regime: {'HIGH' if df['high_risk'].iloc[-1] else 'LOW'}")

    visualize_stock(df, ticker, forecast_val, risk_thresh)
