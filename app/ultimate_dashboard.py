import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(layout="wide", page_title="Ultimate NIFTY Risk v2")
st.title("🌟 Ultimate NIFTY 50 Risk Platform")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 NIFTY Core", "⚠️ VaR", "🎯 Events", "🌍 Multi‑Asset"]
)

# ---------- TAB 1: NIFTY CORE ----------
with tab1:
    df = pd.read_csv("data/processed/nifty50_all_vols.csv",
                     index_col=0, parse_dates=True)

    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start", df.index.min().date())
    end_date = col2.date_input("End", df.index.max().date())
    vol_col = st.selectbox("Vol measure",
                           ["roll_20d", "roll_60d", "roll_120d"])

    mask = (df.index.date >= start_date) & (df.index.date <= end_date)
    d = df.loc[mask]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=d.index, y=d["close"],
                             name="NIFTY 50",
                             line=dict(color="blue")),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=d.index, y=d[vol_col] * 100,
                             name=f"{vol_col} %",
                             line=dict(color="orange")),
                  secondary_y=True)
    fig.update_yaxes(title_text="Index level", secondary_y=False)
    fig.update_yaxes(title_text="Volatility %", secondary_y=True)
    fig.update_layout(height=500, title="Price vs Rolling Volatility")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg vol", f"{d[vol_col].mean() * 100:.1f}%")
    c2.metric("Max vol", f"{d[vol_col].max() * 100:.1f}%")
    c3.metric("Recent 20d",
              f"{d[vol_col].tail(20).mean() * 100:.1f}%")

# ---------- TAB 2: VaR ----------
with tab2:
    st.subheader("VaR Analysis (daily 95%)")
    if Path("data/processed/nifty_var.csv").exists():
        var_df = pd.read_csv("data/processed/nifty_var.csv",
                             index_col=0, parse_dates=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=var_df.index,
                                 y=var_df["historical_var"] * 100,
                                 name="Historical VaR 95%",
                                 line=dict(color="green")))
        fig.update_layout(height=400,
                          title="Rolling Historical VaR (1‑day, 95%)",
                          yaxis_title="VaR %")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(var_df.tail(), use_container_width=True)
    else:
        st.info("Run `python src/var.py` to generate VaR data.")

# ---------- TAB 3: EVENTS ----------
with tab3:
    st.subheader("Major Events Impact on Volatility")
    if Path("reports/event_analysis.csv").exists():
        ev = pd.read_csv("reports/event_analysis.csv")
        st.dataframe(ev.style.format({
            "Vol_Before_20d_%": "{:.1f}%",
            "Vol_After_20d_%": "{:.1f}%",
            "Change_pct": "{:.0f}%"
        }), use_container_width=True)
        st.markdown(
            "**Insight:** COVID crash drove vol up ~172%, "
            "RBI rate cuts reduced vol ~61%."
        )
    else:
        st.info("Run `python src/events.py` to generate event table.")

# ---------- TAB 4: MULTI‑ASSET ----------
with tab4:
    st.subheader("Multi‑Asset Comparison: NIFTY, BankNifty, SPY, IndiaVIX")
    price_path = Path("data/processed/multi_asset_prices.csv")
    ret_path = Path("data/processed/multi_asset_returns.csv")

    if price_path.exists() and ret_path.exists():
        prices = pd.read_csv(price_path, index_col=0, parse_dates=True)
        rets = pd.read_csv(ret_path, index_col=0, parse_dates=True)

        assets = list(prices.columns)
        selected = st.multiselect("Select assets",
                                  assets,
                                  default=assets)

        if selected:
            norm = prices[selected] / prices[selected].iloc[0] * 100
            fig_p = px.line(norm,
                            x=norm.index,
                            y=norm.columns,
                            title="Normalized Prices (100 = start)")
            fig_p.update_layout(height=450,
                                yaxis_title="Index (normalized)")
            st.plotly_chart(fig_p, use_container_width=True)

            corr = rets[selected].corr()
            fig_c = px.imshow(corr,
                              text_auto=True,
                              color_continuous_scale="RdBu_r",
                              zmin=-1, zmax=1,
                              title="Return Correlation")
            st.plotly_chart(fig_c, use_container_width=True)

            st.caption("Data from Yahoo Finance: NIFTY50, BankNifty, "
                       "SPY, IndiaVIX.")
        else:
            st.info("Select at least one asset to plot.")
    else:
        st.info("Run `python src/multi_asset.py` to download multi‑asset data.")