import yfinance as yf
import pandas as pd
from pathlib import Path

def download_nifty_data(start_date="2010-01-01", end_date="2026-03-21"):
    """Download NIFTY 50 (^NSEI) data from Yahoo Finance"""
    ticker = "^NSEI"
    print(f"📥 Downloading {ticker} from {start_date} to {end_date}...")
    
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    if data.empty:
        raise ValueError("No data downloaded - check ticker or dates")
    
    # Save raw
    raw_path = Path("data/raw/nifty50_yahoo_raw.csv")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(raw_path)
    
    print(f"✅ Shape: {data.shape}")
    print(f"📅 Range: {data.index.min().date()} to {data.index.max().date()}")
    print(f"💾 Saved: {raw_path}")
    
    return data

if __name__ == "__main__":
    df = download_nifty_data()
    print(df.head())
