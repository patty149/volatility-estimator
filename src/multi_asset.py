import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

ASSETS = {
    'NIFTY50': '^NSEI',
    'BankNifty': '^NSEBANK',
    'SPY': 'SPY',
    'IndiaVIX': '^INDIAVIX'
}

def download_multi_asset(start="2015-01-01", end=None):
    """Download multi-asset close prices + log returns with flexible columns."""
    print("📥 Downloading:", ASSETS)
    data = yf.download(list(ASSETS.values()), start=start, end=end, progress=False)

    # Handle both single-index and MultiIndex columns
    if isinstance(data.columns, pd.MultiIndex):
        close = data['Close']
        close.columns = list(ASSETS.keys())
    else:
        # Single asset fallback or flat columns
        close = data.rename(columns={v: k for k, v in ASSETS.items() if v in data.columns})

    close = close.dropna(how='all')
    close = close.sort_index()

    # Log returns
    returns = np.log(close / close.shift(1))

    Path("data/processed").mkdir(exist_ok=True)
    close.to_csv("data/processed/multi_asset_prices.csv")
    returns.to_csv("data/processed/multi_asset_returns.csv")

    print("✅ Multi-asset prices shape:", close.shape)
    print("Columns:", list(close.columns))
    return close, returns

if __name__ == "__main__":
    prices, returns = download_multi_asset()
