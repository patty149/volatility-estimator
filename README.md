# Volatility Estimator: NIFTY 50 Risk Analytics Tool

A production‑ready volatility analysis tool for NIFTY 50 with:
- Multiple volatility measures (historical, rolling, EWMA)
- Event‑based risk analysis
- Interactive Streamlit dashboard

## Quick start
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Structure
volatility-estimator/
├── notebooks/ # Exploratory analysis
├── src/ # Production code
├── app/ # Streamlit dashboard
├── data/ # Processed datasets
└── reports/ # Figures and notes

text

## Key Features
- **Data**: 15+ years NIFTY 50 daily data from Yahoo Finance (^NSEI)
- **Volatility**: Historical, Rolling (20/60/120d), EWMA (λ=0.94, 0.97)
- **Events**: Pre/post analysis around market shocks
- **Dashboard**: Interactive risk visualization

