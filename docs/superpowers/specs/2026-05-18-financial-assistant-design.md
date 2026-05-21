# Financial Assistant — Design Spec
**Date:** 2026-05-18
**Stack:** Python, Streamlit, Node.js, SQLite, LSTM (TensorFlow/Keras)

---

## Purpose
A full-stack portfolio project displaying real-time S&P 500 stock data with a 30-day LSTM volatility forecast. Key goal: make AI output readable and actionable for a non-technical user.

---

## Architecture

Three independent layers:

```
Node.js API (port 3001)
    ↓  HTTP
Python: SQLite + LSTM model
    ↓  reads DB
Streamlit Dashboard
```
<!--  -->
### Layer 1 — Node.js API Server (`api/`)
- **Framework:** Express.js
- **Package:** `yahoo-finance2` for S&P 500 data (free, no API key)
- **Endpoints:**
  - `GET /api/live` → `{ price, change, change_pct, timestamp }`
  - `GET /api/historical` → array of `{ date, open, high, low, close, volume }` (5 years)
- **Port:** 3001

### Layer 2 — Python: Data Sync + LSTM (`db/` + `model/`)

**SQLite database** (`db/sp500.db`):
- `historical_prices(date TEXT PRIMARY KEY, open, high, low, close, volume)`
- `predictions(run_date TEXT, forecast_date TEXT PRIMARY KEY, predicted_close REAL)`

**Data sync** (`db/sync_data.py`):
- Calls `GET /api/historical`, upserts into `historical_prices`
- Calls `GET /api/live`, prints current price

**LSTM model** (`model/`):
- Input: 60-day lookback window of normalized closing prices
- Architecture: 2 LSTM layers (50 units each) → Dense(1)
- Output: 30-day forecast of closing prices
- Training data: 5 years of daily S&P 500 closes from `historical_prices`
- Saved to `model/sp500_model.h5`
- `train.py` — train and save model
- `predict.py` — load model, generate 30-day forecast, write to `predictions` table

### Layer 3 — Streamlit Dashboard (`dashboard/app.py`)

**Layout:** Side-by-side (Layout C)
- **Left panel (2/3 width):**
  - Live price header: current price, daily change, % change (auto-refreshes every 60s)
  - Historical Plotly line chart with time range buttons: 1M / 3M / 1Y / 5Y
- **Right panel (1/3 width):**
  - 30-day forecast chart: last 30 days actual data (blue) + 30 days predicted (orange)
  - Clear label distinguishing historical vs predicted

**Data source:** Reads directly from SQLite (`sp500.db`)

---

## File Structure

```
Financial_Assistant/
├── api/
│   ├── server.js           ← Express API server
│   └── package.json
├── model/
│   ├── train.py            ← Train LSTM, save sp500_model.h5
│   ├── predict.py          ← Load model, write predictions to DB
│   └── sp500_model.h5      ← Saved model (generated, not committed)
├── db/
│   ├── init_db.py          ← Create SQLite tables
│   ├── sync_data.py        ← Fetch from Node.js API, upsert to DB
│   └── sp500.db            ← SQLite database (generated, not committed)
├── dashboard/
│   └── app.py              ← Streamlit app
├── requirements.txt        ← Python dependencies
├── .gitignore
└── README.md
```

---

## Dependencies

**Node.js** (`api/package.json`):
- `express`
- `yahoo-finance2`

**Python** (`requirements.txt`):
- `streamlit`
- `plotly`
- `pandas`
- `numpy`
- `tensorflow`
- `scikit-learn`
- `requests`
- `sqlite3` (built-in)

---

## Running the Project

1. Start Node.js API: `cd api && node server.js`
2. Init DB: `python db/init_db.py`
3. Sync data: `python db/sync_data.py`
4. Train model: `python model/train.py`
5. Generate predictions: `python model/predict.py`
6. Launch dashboard: `streamlit run dashboard/app.py`

---

## Verification
- Node.js API returns valid JSON at `http://localhost:3001/api/live` and `/api/historical`
- `sp500.db` contains rows in both tables after sync + predict steps
- Streamlit dashboard loads at `http://localhost:8501` showing live price, historical chart, and forecast chart
- Forecast chart shows blue (actual) and orange (predicted) lines with visible 30-day horizon
