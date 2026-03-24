import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(layout="wide")
st.title("🔥 NIFTY 50 Risk Dashboard v2")

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/nifty50_all_vols.csv", index_col=0, parse_dates=True)

df = load_data()

# FIXED date inputs (no slider type issues)
col1, col2 = st.columns(2)
start_date = col1.date_input("Start Date", df.index.min().date())
end_date = col2.date_input("End Date", df.index.max().date())

vol_measure = st.selectbox("Volatility", ['roll_20d', 'roll_60d', 'roll_120d'])

# Filter
mask = (df.index.date >= start_date) & (df.index.date <= end_date)
df_f = df.loc[mask]

# Plot
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_f.index, y=df_f['close'], name='NIFTY', line=dict(color='blue')), secondary_y=False)
fig.add_trace(go.Scatter(x=df_f.index, y=df_f[vol_measure]*100, name=f'{vol_measure} %', line=dict(color='red')), secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df_f[['close', vol_measure]].describe())
