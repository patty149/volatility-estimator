import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path

st.set_page_config(layout="wide", page_title="NIFTY Risk Pro")
st.title("🏆 NIFTY 50 Risk Analytics Pro")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Events", "⚠️ VaR"])

with tab1:
    # Load + controls
    df = pd.read_csv("data/processed/nifty50_all_vols.csv", index_col=0, parse_dates=True)
    
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start", df.index.min().date())
    end_date = col2.date_input("End", df.index.max().date())
    
    vol_measures = ['roll_20d', 'roll_60d', 'roll_120d']
    vol_type = st.selectbox("Vol Measure", vol_measures)
    
    # Filter
    mask = (df.index.date >= start_date) & (df.index.date <= end_date)
    df_f = df.loc[mask]
    
    # Interactive chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df_f.index, y=df_f['close'], name='NIFTY 50', 
                            line=dict(color='#1f77b4', width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_f.index, y=df_f[vol_type]*100, name=f'{vol_type.upper()} %', 
                            line=dict(color='#ff7f0e', width=2)), secondary_y=True)
    
    fig.update_layout(height=500, title="Price vs Rolling Volatility")
    st.plotly_chart(fig, use_container_width=True)
    
    # Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Vol", f"{df_f[vol_type].mean()*100:.1f}%")
    col2.metric("Max Vol", f"{df_f[vol_type].max()*100:.1f}%")
    col3.metric("Recent 20d", f"{df_f[vol_type].tail(20).mean()*100:.1f}%")

with tab2:
    st.subheader("Major Events Impact")
    events_df = pd.read_csv("reports/event_analysis.csv")
    st.dataframe(events_df.style.format({
        'Vol_Before_20d_%': '{:.1f}%',
        'Vol_After_20d_%': '{:.1f}%',
        'Change_pct': '{:.0f}%'
    }), use_container_width=True)
    
    st.caption("**Insight**: RBI policy response cut vol 61% post‑COVID peak")

with tab3:
    st.subheader("VaR Analysis")
    try:
        var_df = pd.read_csv("data/processed/nifty_var.csv", index_col=0, parse_dates=True)
        fig_var = go.Figure()
        fig_var.add_trace(go.Scatter(x=var_df.index, y=var_df['historical_var']*100, 
                                    name='Historical VaR 95%', line=dict(color='green')))
        st.plotly_chart(fig_var, title="Rolling 1‑day 95% VaR")
    except:
        st.info("🔄 Run `python src/var.py` first")
