import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

def full_pipeline():
    """Download → clean → log returns → save (no CSV parsing issues)"""
    
    # Download FRESH data (avoid CSV weirdness)
    print("📥 Downloading fresh NIFTY 50 data...")
    ticker = "^NSEI"
    data = yf.download(ticker, start="2010-01-01", end="2026-03-21", progress=False)
    
    # Flatten columns immediately
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
    
    # Standardize names
    data = data.rename(columns={
        'Close': 'close', 'Open': 'open', 
        'High': 'high', 'Low': 'low', 
        'Volume': 'volume', 'Adj Close': 'adj_close'
    })
    
    # Log returns
    data['log_return'] = np.log(data['close'] / data['close'].shift(1))
    
    print(f"✅ Pipeline complete: {len(data)} rows")
    print(f"📅 {data.index.min().date()} to {data.index.max().date()}")
    print("\nColumns:", data.columns.tolist())
    print("\nSample:")
    print(data[['close', 'log_return']].head())
    
    # Save clean versions
    Path("data/processed").mkdir(exist_ok=True)
    data.to_csv("data/processed/nifty50_pipeline.csv")
    print("\n💾 Saved: data/processed/nifty50_pipeline.csv")
    
    return data

if __name__ == "__main__":
    df = full_pipeline()
