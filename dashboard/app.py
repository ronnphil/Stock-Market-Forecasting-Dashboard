import streamlit as st
import sqlite3
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from dashboard.charts import build_historical_chart, build_forecast_chart

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'sp500.db')
API_BASE = 'http://localhost:3001/api'

st.set_page_config(page_title='S&P 500 Dashboard', layout='wide')
st.title('S&P 500 Dashboard')

@st.cache_data(ttl=60)
def get_live():
    try:
        r = requests.get(f'{API_BASE}/live', timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_historical(days=365):
    cutoff = (datetime.today() - timedelta(days=days)).strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        'SELECT date, close FROM historical_prices WHERE date >= ? ORDER BY date',
        conn, params=(cutoff,)
    )
    conn.close()
    return df

@st.cache_data(ttl=3600)
def get_predictions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        'SELECT forecast_date, predicted_close FROM predictions ORDER BY forecast_date',
        conn
    )
    conn.close()
    return df

live = get_live()
if live:
    color = 'green' if live['change'] >= 0 else 'red'
    arrow = '▲' if live['change'] >= 0 else '▼'
    st.markdown(
        f"### {arrow} **${live['price']:,.2f}** &nbsp; "
        f"<span style='color:{color}'>{live['change']:+.2f} "
        f"({live['change_pct']:+.2f}%)</span> today",
        unsafe_allow_html=True
    )
else:
    st.warning('Live price unavailable — is the Node.js API running on port 3001?')

st.divider()

actual = get_historical(30)
left, right = st.columns([2, 1])

with left:
    st.subheader('Historical Price')
    range_map = {'1M': 30, '3M': 90, '1Y': 365, '5Y': 1825}
    selected = st.radio('Range', list(range_map.keys()), horizontal=True, index=2)
    hist = get_historical(range_map[selected])
    if not hist.empty:
        st.plotly_chart(build_historical_chart(hist), use_container_width=True)
    else:
        st.info('No historical data — run: python db/sync_data.py')

with right:
    st.subheader('30-Day Forecast')
    preds = get_predictions()
    if not preds.empty:
        st.plotly_chart(build_forecast_chart(actual, preds), use_container_width=True)
        st.caption('Blue = actual · Orange dashed = LSTM prediction')
    else:
        st.info('No predictions — run: python model/predict.py')

st.caption(f"Live price refreshes every 60s · Last loaded: {datetime.now().strftime('%H:%M:%S')}")
