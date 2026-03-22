import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import norm  # Now installed

def compute_var_historical(df, confidence=0.95, window=252):
    """Historical & Parametric VaR"""
    returns = df['log_return'].dropna()
    
    # Parametric (normal assumption)
    mu_daily = returns.mean()
    sigma_daily = returns.std()
    z = norm.ppf(confidence)
    parametric_var_pct = -(mu_daily + z * sigma_daily)
    
    # Historical VaR (percentile)
    historical_var_pct = -returns.rolling(window).quantile(1-confidence)
    
    print(f"�� VaR Analysis (daily, {confidence*100}% confidence)")
    print(f"Mean daily return:  {mu_daily*100:.3f}%")
    print(f"Daily vol:         {sigma_daily*100:.2f}%")
    print(f"Parametric VaR:    {parametric_var_pct*100:.2f}%")
    print(f"Historical VaR:    {historical_var_pct.iloc[-1]*100:.2f}% (recent)")
    
    return pd.DataFrame({
        'parametric_var': parametric_var_pct,
        'historical_var': historical_var_pct
    })

if __name__ == "__main__":
    df = pd.read_csv("data/processed/nifty50_pipeline.csv", index_col=0, parse_dates=True)
    var_df = compute_var_historical(df)
    var_df.to_csv("data/processed/nifty_var.csv")
    print("\n💾 data/processed/nifty_var.csv")
