import pandas as pd
import numpy as np
from pathlib import Path

def load_processed_data():
    path = Path("data/processed/nifty50_pipeline.csv")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df.sort_index()

def compute_historical_volatility(df, window=None):
    """Historical volatility σ = std(returns) × √252"""
    returns = df['log_return'].dropna()
    
    if window:
        return returns.rolling(window=window, min_periods=window//2).std() * np.sqrt(252)
    else:
        return returns.std() * np.sqrt(252)

def compute_ewma_volatility(df, span=30):
    """EWMA volatility using pandas ewm (industry standard)"""
    returns = df['log_return'].dropna()
    # span=30 → λ = 1 - 2/(span+1) ≈ 0.94
    ewma_var = returns.ewm(span=span).var()
    return np.sqrt(ewma_var) * np.sqrt(252)

def full_volatility_suite():
    df = load_processed_data()
    
    # Historical vols
    hist_full = compute_historical_volatility(df)
    
    # Rolling windows
    roll_windows = [20, 60, 120]
    rolling_vols = {f'roll_{w}d': compute_historical_volatility(df, w) 
                   for w in roll_windows}
    
    # EWMA (different decay via span parameter)
    ewma_spans = [20, 40]  # Fast (0.95), Slow (0.975)
    ewma_vols = {f'ewma_span{w}': compute_ewma_volatility(df, w) 
                for w in ewma_spans}
    
    # Combine
    results = pd.DataFrame(index=df.index, data={'close': df['close']})
    results['hist_full'] = hist_full
    results = pd.concat([results, pd.DataFrame(rolling_vols)], axis=1)
    results = pd.concat([results, pd.DataFrame(ewma_vols)], axis=1)
    
    # Save
    output_path = Path("data/processed/nifty50_all_vols.csv")
    output_path.parent.mkdir(exist_ok=True)
    results.to_csv(output_path)
    
    print("✅ ALL volatilities computed!")
    print(f"📊 Shape: {results.shape}")
    print("\nRecent values (% annualized):")
    print(results.filter(like='roll').tail())
    
    return results

if __name__ == "__main__":
    vols = full_volatility_suite()
