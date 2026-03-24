# NIFTY 50 Volatility & VaR Dashboard

End‑to‑end **risk analytics platform** for the NIFTY 50 index and related markets.  
The project downloads 15+ years of daily data, computes multiple volatility and VaR measures, performs event‑based risk analysis, and serves everything through an interactive Streamlit dashboard.

---

## 1. Motivation

Volatility is the core risk metric in equities: it tells you how violently prices move, how much capital you might lose in a normal day, and how crises differ from calm regimes.[web:39][web:149]  
Most tutorials stop at a single historical volatility number. This project goes further:

- Multiple time‑scale vol (20/60/120‑day rolling, EWMA).  
- VaR (parametric and historical).  
- Event study around **COVID**, **RBI policy**, **Ukraine war**, etc.  
- Multi‑asset view: **NIFTY 50**, **BankNifty**, **SPY**, **India VIX**.[web:55][web:46][web:151]

The goal is to build something a **risk / product / quant team could actually use**.

---

## 2. Project structure

```text
volatility-estimator/
├── app/
│   ├── streamlit_app.py         # Simple NIFTY dashboard
│   ├── streamlit_pro.py         # 3‑tab Pro app (Core, Events, VaR)
│   └── ultimate_dashboard.py    # 4‑tab app (Core, VaR, Events, Multi‑Asset)
├── src/
│   ├── data_loader.py           # yfinance download helpers (^NSEI etc.)
│   ├── data_pipeline.py         # One‑shot pipeline: download→clean→returns
│   ├── preprocessing.py         # Cleaning, log returns
│   ├── volatility.py            # Hist vol, rolling vol, EWMA vol
│   ├── events.py                # Event study (COVID, RBI, Ukraine,…)
│   ├── var.py                   # Parametric + historical 1‑day VaR
│   ├── garch.py                 # GARCH(1,1) volatility model
│   └── multi_asset.py           # NIFTY50 / BankNifty / SPY / IndiaVIX loader
├── data/
│   ├── raw/                     # Direct Yahoo Finance CSVs
│   └── processed/               # Clean series & risk metrics
├── reports/
│   ├── figures/                 # PNG charts (price+vol, GARCH, etc.)
│   └── event_analysis.csv       # Pre/post event volatility summary
├── notebooks/                   # Optional exploratory notebooks
├── requirements.txt
└── README.md
```

---

## 3. Data & preprocessing

### 3.1 Assets

- **NIFTY 50** (`^NSEI`) – main Indian equity benchmark.[web:55]  
- **BankNifty** (`^NSEBANK`) – financial sector.  
- **SPY** (`SPY`) – S&P 500 ETF proxy.  
- **India VIX** (`^INDIAVIX`) – implied volatility index for NIFTY options.[web:40][web:151]

### 3.2 Pipeline

Main pipeline (NIFTY):

1. Download daily OHLCV via `yfinance`.  
2. Clean column names and sort dates.  
3. Compute **log returns**:  
   \[
   r_t = \ln(P_t / P_{t-1})
   \]
4. Save to `data/processed/nifty50_pipeline.csv`.

Multi‑asset:

- Download all four tickers in one call.  
- Align their close prices on a common date index.  
- Compute log returns and save:
  - `multi_asset_prices.csv`  
  - `multi_asset_returns.csv`.

---

## 4. Volatility & VaR metrics

### 4.1 Historical and rolling volatility

For daily log returns \(r_t\), daily volatility is:

\[
\sigma_\text{daily} = \text{std}(r_t)
\]

Annualized volatility:

\[
\sigma_\text{annual} = \sigma_\text{daily} \sqrt{252}
\]

Implemented:

- **Full‑sample volatility** (one number for 2010–today).  
- **Rolling windows**: 20, 60, 120 days:
  - `roll_20d`, `roll_60d`, `roll_120d` in `nifty50_all_vols.csv`.
  - 20d ≈ 1‑month, reacts fast.  
  - 120d ≈ 6‑month, smoother regime view.[web:36][web:41]

### 4.2 EWMA volatility

Exponentially Weighted Moving Average (EWMA) gives more weight to recent returns:[web:48]

- Implemented via `pandas.Series.ewm(span=…).var()` and square‑rooted.  
- Stored as `ewma_span20`, `ewma_span40`:
  - Fast EWMA ≈ RiskMetrics‑style short memory.  
  - Slow EWMA ≈ longer memory.

### 4.3 VaR (Value at Risk)

**Question VaR answers**:  
> “On a normal day, with 95% confidence, how much might I lose at most?”

Computed 1‑day 95% VaR using:[web:73][web:76][web:85]

- **Parametric VaR** (normal assumption)  
  \[
  \text{VaR}_{0.95} = -(\mu + z_{0.95}\sigma)
  \]
  where \(\mu\) and \(\sigma\) are daily mean and std, and \(z_{0.95}\approx 1.645\).

- **Historical VaR**  
  - Take rolling 252‑day window of actual returns.  
  - VaR = 5th percentile (worst 5% of days).

Output stored in `data/processed/nifty_var.csv`, and visualized in the **VaR tab**.

---

## 5. Event‑based risk analysis

Using `src/events.py`, the project quantifies how volatility changed around key events:

- **COVID Crash (2020‑03‑23)** – NIFTY bottom during pandemic.[web:60][web:147][web:153]  
- **RBI emergency rate cuts / liquidity actions (2020‑05‑22)** – policy response.[web:59][web:62]  
- **Russia–Ukraine war (2022‑02‑24)** – global macro shock.[web:61]

For each event:

1. Define a pre and post window (e.g., 90 calendar days).  
2. Compute average **20‑day rolling volatility** before and after.  
3. Report pre/post levels and percent change.

Example results (illustrative):

- COVID crash: 20d vol jumps from ~18.6% → ~50.5% (**+172%**).  
- RBI support: vol falls from ~51.3% → ~20.1% (**−61%**).  
- Ukraine war: vol rises from ~17.7% → ~21.9% (**+24%**).

Results saved in `reports/event_analysis.csv` and shown in the **Events tab**.

Interpretation:

- Crises move the market into *high‑volatility regimes* (risk and VaR spike).  
- Policy interventions can pull the market back into calmer regimes (lower vol, lower VaR).

---

## 6. GARCH volatility model

To go beyond descriptive vol, the project includes a **GARCH(1,1)** model:[web:147][web:153]

\[
\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2
\]

- \(\epsilon_{t-1}\): last period’s return shock.  
- \(\sigma_{t-1}\): last period’s variance.  
- Parameters typically satisfy \(\alpha + \beta \approx 1\) for persistent volatility.

Using the `arch` package:

- Fit GARCH(1,1) to NIFTY daily returns.  
- Print parameters (ω, α, β).  
- Generate a short‑horizon volatility forecast and overlay on recent returns.  
- Save figure as `reports/figures/garch_forecast.png`.

This demonstrates ability to **model and forecast** volatility, not just measure it.

---

## 7. Multi‑asset analytics

`src/multi_asset.py` downloads and prepares:

- NIFTY 50 (`^NSEI`)  
- BankNifty (`^NSEBANK`)  
- SPY (US equity proxy)  
- India VIX (`^INDIAVIX`)[web:46][web:151]

Dashboard features:

- **Normalized price chart**: all assets scaled to 100 at start date to compare cumulative performance.  
- **Return correlation heatmap**:
  - High NIFTY vs BankNifty correlation (same market).  
  - Moderate NIFTY vs SPY correlation (global linkage).[web:61][web:149]  
  - Strong negative correlation between India VIX and NIFTY/BankNifty (vol spikes when markets fall).[web:46][web:151]

This provides a **portfolio / cross‑asset risk view** for Indian equities.

---

## 8. Streamlit dashboards

There are three Streamlit apps:

1. `app/streamlit_app.py` – simple single‑page NIFTY chart (price + rolling vol).  
2. `app/streamlit_pro.py` – **3 tabs**:
   - Core: price vs chosen vol measure (20/60/120d).  
   - Events: event analysis table + commentary.  
   - VaR: VaR time series and summary stats.
3. `app/ultimate_dashboard.py` – **4 tabs**:
   - **NIFTY Core** – interactive price vs vol + summary metrics.  
   - **VaR** – rolling historical VaR visualization.  
   - **Events** – event‑driven volatility regime comparisons.  
   - **Multi‑Asset** – normalized prices + correlation heatmap for NIFTY50, BankNifty, SPY, IndiaVIX.

### Run locally

```bash
# Set up env (once)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate data
python src/data_pipeline.py        # NIFTY pipeline
python src/volatility.py          # Vol metrics
python src/events.py              # Event analysis
python src/var.py                 # VaR series
python src/multi_asset.py         # Multi‑asset data
python src/garch.py               # GARCH model & plot (optional)

# Launch dashboard
streamlit run app/ultimate_dashboard.py
```

---

## 9. How this maps to risk & product work

This project demonstrates:

- **Quant skills**: volatility estimation, VaR, event study, GARCH modeling for NIFTY.[web:36][web:48][web:73][web:147]  
- **Engineering discipline**: modular `src/`, virtual env, clear data folders, reproducible scripts.  
- **Product thinking**: multi‑tab dashboard tailored for risk teams (controls, charts, tables).  
- **Market understanding**: connects COVID, RBI policy, wars, and cross‑market linkages to volatility regimes.

It is suitable as a **flagship project** for Master’s applications and roles in **risk, quant analytics, or product analytics** in Indian or global equity contexts.

