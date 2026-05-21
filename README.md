# Stock Market Forecasting Dashboard

Full-stack S&P 500 dashboard with real-time data and LSTM-powered 30-day market forecasting.

**Stack:** Python · Streamlit · Node.js · SQLite · TensorFlow/Keras

---

## Overview

- Built a full-stack web app displaying real-time S&P 500 stock data with AI-powered market trend forecasting
- Key focus: making complex AI output readable and actionable for a non-technical user
- Side-by-side layout: historical price chart (left) + 30-day LSTM forecast (right)


---

## Demo
<img width="1889" height="982" alt="image" src="https://github.com/user-attachments/assets/4863135a-40b0-49f9-a83c-30d71443869a" />
> Live price refreshes every 60s · Historical chart supports 1M / 3M / 1Y / 5Y ranges · Forecast updates daily

---

## How It Works

```
Node.js API (port 3001)        →   fetches live + historical S&P 500 data (Yahoo Finance)
Python: SQLite + LSTM model    →   stores data, trains model, generates 30-day predictions
Streamlit Dashboard            →   reads SQLite and renders the UI
```

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+

### 1. Clone the repo

```bash
git clone https://github.com/ronnphil/Stock-Market-Forecasting-Dashboard.git
cd Stock-Market-Forecasting-Dashboard
```

### 2. Install dependencies

```bash
# Python
pip install -r requirements.txt

# Node.js
cd api && npm install && cd ..
```

### 3. Set up the database

```bash
python db/init_db.py
python db/sync_data.py
```

### 4. Train the model and generate predictions

```bash
python model/train.py      # takes ~2 minutes on CPU
python model/predict.py
```

### 5. Run the app

Open two terminals from the project root:

**Terminal 1 — Data API:**
```bash
cd api
node server.js
```

**Terminal 2 — Dashboard:**
```bash
streamlit run dashboard/app.py
```

Open **http://localhost:8501** in your browser.

---

## Project Structure

```
├── api/
│   └── server.js          # Express API — /api/live and /api/historical
├── db/
│   ├── init_db.py          # Create SQLite tables
│   └── sync_data.py        # Fetch data from Node API → SQLite
├── model/
│   ├── train.py            # Train LSTM model
│   └── predict.py          # Generate 30-day forecast
├── dashboard/
│   ├── charts.py           # Plotly chart builders
│   └── app.py              # Streamlit UI
└── tests/                  # 13 unit tests (pytest + jest)
```

---

## Highlights

**UI — Streamlit Dashboard**
- Structured layout around user flow: overview → detail → forecast
- Color contrast distinguishes historical (blue) vs predicted (orange) data
- AI output surfaced directly — no data science background needed to interpret it

**Backend — Node.js Data Pipeline**
- Express API fetches live and 5-year historical S&P 500 data via Yahoo Finance (free, no API key)
- SQLite stores historical prices and predictions locally

**AI — LSTM Forecasting Model**
- 60-day lookback window · 2 LSTM layers (50 units each) · trained on 5 years of daily closes
- Autoregressive rollout generates 30 weekday predictions, skipping weekends

---

## Key Takeaway

Building the AI model was the straightforward part. The real challenge was designing the dashboard so the predictions were actually interpretable — choosing the right chart, the right labels, and the right layout so a user didn't need a data science background to understand what the model was telling them.
