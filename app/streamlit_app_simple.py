import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")
st.title("🚀 NIFTY 50 Volatility Dashboard")

# Load data (no cache)
df = pd.read_csv("data/processed/nifty50_all_vols.csv", 
                index_col=0, parse_dates=True)

# Simple controls
col1, col2 = st.columns(2)
vol_type = col1.selectbox("Vol Measure", ['roll_20d', 'roll_60d', 'roll_120d'])
start_date = col1.date_input("Start", df.index.min().date())
end_date = col2.date_input("End", df.index.max().date())

# Filter
mask = (df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))
df_filtered = df.loc[mask]

# Chart
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered['close'], 
                        name='NIFTY 50', line=dict(color='blue', width=2)), 
              secondary_y=False)
fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered[vol_type]*100, 
                        name=f'{vol_type} (%)', line=dict(color='red', width=2)), 
              secondary_y=True)

fig.update_layout(title="Price vs Volatility", height=600)
fig.update_yaxes(title="NIFTY Level", secondary_y=False)
fig.update_yaxes(title="Volatility %", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

# Metrics
col1, col2 = st.columns(2)
col1.metric("Avg Vol (period)", f"{df_filtered[vol_type].mean()*100:.1f}%")
col2.metric("Max Vol (period)", f"{df_filtered[vol_type].max()*100:.1f}%")

st.dataframe(df_filtered[['close', vol_type]].tail(), use_container_width=True)
