import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

def load_all_vols():
    path = Path("data/processed/nifty50_all_vols.csv")
    return pd.read_csv(path, index_col=0, parse_dates=True)

def plot_price_and_volatility():
    """Main chart: NIFTY price + multiple vol measures"""
    df = load_all_vols()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), 
                                   gridspec_kw={'height_ratios': [2, 1]})
    
    # Top: Price
    ax1.plot(df.index, df['close'], color='black', linewidth=1.5, label='NIFTY 50')
    ax1.set_title('NIFTY 50 Price & Volatility (2010-2026)', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Index Level', fontsize=12)
    ax1.grid(alpha=0.3)
    ax1.legend()
    
    # Bottom: Volatility measures (convert to % for readability)
    vols = df.filter(like='roll') * 100  # % scale
    for col in vols.columns:
        ax2.plot(df.index, vols[col], label=col.replace('_', ' ').title(), linewidth=1.2)
    
    ax2.set_title('Rolling Volatility (20d, 60d, 120d)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Annualized Volatility (%)', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # Format x-axis
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig('reports/figures/nifty_price_vol.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("💾 Saved: reports/figures/nifty_price_vol.png")

if __name__ == "__main__":
    plot_price_and_volatility()
