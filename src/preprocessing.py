import pandas as pd
import numpy as np
from pathlib import Path

def load_raw_data_flexible(raw_path="data/raw/nifty50_yahoo_raw.csv"):
    """Load ANY yfinance CSV - handles multiindex weirdness"""
    # Read without assumptions
    df = pd.read_csv(raw_path)
    
    # Find date column (usually first or named 'Date')
    date_col = None
    for col in df.columns:
        if 'date' in col.lower():
            date_col = col
            break
    if date_col is None:
        date_col = df.columns[0]  # Assume first column
    
    # Set date index
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    df.index.name = 'date'
    
    # Drop ticker level if multiindex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)  # Drop '^NSEI' level
    
    # Standardize column names
    df = df.rename(columns={
        col.lower(): key for key, col in {
            'close': ['close', 'adj close'],
            'open': 'open',
            'high': 'high', 
            'low': 'low',
            'volume': 'volume'
        }.items()
    }, errors='ignore')
    
    # Keep only OHLCV + sort
    keep_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
    df = df[[col for col in keep_cols if col in df.columns]]
    df = df.sort_index()
    
    # Lowercase for consistency
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    
    print(f"📊 Loaded: {len(df)} rows")
    print("Columns:", df.columns.tolist())
    return df

def compute_log_returns(df):
    """Log returns from close price"""
    df = df.copy()
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    return df

if __name__ == "__main__":
    df = load_raw_data_flexible()
    df_returns = compute_log_returns(df)
    
    print(f"\n📅 Range: {df_returns.index.min().date()} to {df_returns.index.max().date()}")
    print("\nSample data:")
    print(df_returns[['close', 'log_return']].head())
    
    # Save clean version
    processed_path = Path("data/processed/nifty50_clean.csv")
    processed_path.parent.mkdir(exist_ok=True)
    df_returns.to_csv(processed_path)
    print(f"\n💾 Clean data: {processed_path}")
