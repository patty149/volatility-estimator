import pandas as pd
import numpy as np
from arch import arch_model
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def fit_garch_forecast(df, forecast_horizon=30):
    """GARCH(1,1) volatility forecasting"""
    returns = 100 * df['log_return'].dropna()  # % for arch
    
    # Fit GARCH(1,1)
    model = arch_model(returns, vol='Garch', p=1, q=1,
                      rescale=False, mean='Zero')
    fitted = model.fit(disp='off')
    
    # Forecast
    forecast = fitted.forecast(horizon=forecast_horizon)
    vol_forecast = np.sqrt(forecast.variance.iloc[-1])  # Annualized
    
    print("📈 GARCH(1,1) Results")
    print(f"α0: {fitted.params['omega']:.6f}")
    print(f"α1: {fitted.params['alpha[1]']:.3f} (shock impact)")
    print(f"β1: {fitted.params['beta[1]']:.3f} (vol persistence)")
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(returns.tail(252).index, returns.tail(252), label='Returns', alpha=0.7)
    plt.plot(returns.tail(30).index, vol_forecast[-1], 'r-', label='GARCH Forecast', linewidth=3)
    plt.title('GARCH(1,1) Volatility Forecast')
    plt.legend()
    plt.savefig('reports/figures/garch_forecast.png', dpi=300)
    plt.show()
    
    return vol_forecast

if __name__ == "__main__":
    df = pd.read_csv("data/processed/nifty50_pipeline.csv", index_col=0, parse_dates=True)
    forecast = fit_garch_forecast(df)
