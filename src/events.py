import pandas as pd
from pathlib import Path

def load_vol_data():
    path = Path("data/processed/nifty50_all_vols.csv")
    return pd.read_csv(path, index_col=0, parse_dates=True)

def analyze_events():
    """Compare vol before/after major events"""
    df = load_vol_data()
    
    # Key NIFTY events (India context)
    events = {
        'COVID_Crash': '2020-03-23',  # NIFTY bottom
        'RBI_Rate_Cut': '2020-05-22',  # Emergency measures
        'Ukraine_War': '2022-02-24'    # Global shock
    }
    
    results = []
    for name, date in events.items():
        event_date = pd.to_datetime(date)
        
        # 60 trading days before/after
        before = df.loc[event_date - pd.Timedelta(90, 'D'):event_date]['roll_20d'].mean()
        after = df.loc[event_date:event_date + pd.Timedelta(90, 'D')]['roll_20d'].mean()
        
        results.append({
            'Event': name,
            'Date': date,
            'Vol_Before_20d_%': before*100,
            'Vol_After_20d_%': after*100,
            'Change_pct': ((after-before)/before)*100
        })
    
    event_df = pd.DataFrame(results)
    print("📈 Event Analysis (20d rolling vol):")
    print(event_df.round(2))
    
    # Save
    event_df.to_csv('reports/event_analysis.csv', index=False)
    print("\n💾 reports/event_analysis.csv")
    
    return event_df

if __name__ == "__main__":
    events = analyze_events()
