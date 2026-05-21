# Financial Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack S&P 500 dashboard with a Node.js data API, SQLite storage, 30-day LSTM forecast, and a Streamlit side-by-side UI.

**Architecture:** Node.js Express API fetches live + historical S&P 500 data from Yahoo Finance (free). Python syncs that data into SQLite, trains an LSTM on 5 years of closes, writes 30-day predictions back to SQLite. Streamlit reads SQLite and renders a side-by-side layout: historical chart (left) + forecast chart (right).

**Tech Stack:** Node.js, Express, yahoo-finance2, Python 3.10+, TensorFlow/Keras, SQLite3, Streamlit, Plotly, pandas, scikit-learn, pytest, jest, supertest

---

## File Map

| File | Responsibility |
|------|---------------|
| `api/package.json` | Node.js dependencies |
| `api/server.js` | Express API — `/api/live` and `/api/historical` |
| `api/server.test.js` | Jest + supertest tests for the API |
| `db/init_db.py` | Create SQLite tables |
| `db/sync_data.py` | Fetch from Node API, upsert into SQLite |
| `model/train.py` | Load closes from SQLite, train LSTM, save model + scaler |
| `model/predict.py` | Load model, generate 30-day forecast, write to `predictions` table |
| `dashboard/charts.py` | Pure functions: build Plotly figures (no Streamlit imports) |
| `dashboard/app.py` | Streamlit UI — wires live price, charts, and forecast together |
| `tests/conftest.py` | Add project root to sys.path for all pytest tests |
| `tests/test_init_db.py` | Tests for `db/init_db.py` |
| `tests/test_sync_data.py` | Tests for `db/sync_data.py` |
| `tests/test_predict.py` | Tests for `model/predict.py` |
| `tests/test_charts.py` | Tests for `dashboard/charts.py` |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Exclude db, model weights, node_modules |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create the directory structure**

```bash
mkdir -p api db model dashboard tests
```

- [ ] **Step 2: Create `requirements.txt`**

```
streamlit>=1.32.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
tensorflow>=2.13.0
scikit-learn>=1.3.0
requests>=2.31.0
pytest>=7.4.0
```

- [ ] **Step 3: Install Python dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install without errors.

- [ ] **Step 4: Create `.gitignore`**

```
db/sp500.db
model/sp500_model.h5
model/scaler.pkl
node_modules/
__pycache__/
*.pyc
.env
```

- [ ] **Step 5: Create `tests/conftest.py`**

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

- [ ] **Step 6: Commit**

```bash
git init
git add requirements.txt .gitignore tests/conftest.py
git commit -m "chore: project scaffolding"
```

---

## Task 2: Node.js API Server (TDD)

**Files:**
- Create: `api/package.json`
- Create: `api/server.test.js`
- Create: `api/server.js`

- [ ] **Step 1: Create `api/package.json`**

```json
{
  "name": "financial-assistant-api",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.2",
    "yahoo-finance2": "^2.11.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "supertest": "^6.3.0"
  }
}
```

- [ ] **Step 2: Install Node dependencies**

```bash
cd api && npm install
```

Expected: `node_modules/` created, no errors.

- [ ] **Step 3: Write failing tests — `api/server.test.js`**

```javascript
const request = require('supertest');

jest.mock('yahoo-finance2', () => ({
  default: {
    quote: jest.fn().mockResolvedValue({
      regularMarketPrice: 5234.18,
      regularMarketChange: 22.45,
      regularMarketChangePercent: 0.43
    }),
    historical: jest.fn().mockResolvedValue([
      {
        date: new Date('2024-01-02'),
        open: 4742.83,
        high: 4763.13,
        low: 4728.75,
        close: 4742.83,
        volume: 3500000000
      }
    ])
  }
}));

const app = require('./server');

describe('GET /api/live', () => {
  it('returns price, change, change_pct, timestamp', async () => {
    const res = await request(app).get('/api/live');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('price', 5234.18);
    expect(res.body).toHaveProperty('change', 22.45);
    expect(res.body).toHaveProperty('change_pct', 0.43);
    expect(res.body).toHaveProperty('timestamp');
  });
});

describe('GET /api/historical', () => {
  it('returns array of OHLCV objects with string dates', async () => {
    const res = await request(app).get('/api/historical');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body[0]).toMatchObject({
      date: '2024-01-02',
      open: 4742.83,
      close: 4742.83
    });
  });
});
```

- [ ] **Step 4: Run tests — verify they fail**

```bash
cd api && npm test
```

Expected: FAIL — `Cannot find module './server'`

- [ ] **Step 5: Implement `api/server.js`**

```javascript
const express = require('express');
const yahooFinance = require('yahoo-finance2').default;

const app = express();

app.get('/api/live', async (req, res) => {
  try {
    const quote = await yahooFinance.quote('^GSPC');
    res.json({
      price: quote.regularMarketPrice,
      change: quote.regularMarketChange,
      change_pct: quote.regularMarketChangePercent,
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/historical', async (req, res) => {
  try {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setFullYear(startDate.getFullYear() - 5);

    const result = await yahooFinance.historical('^GSPC', {
      period1: startDate,
      period2: endDate,
      interval: '1d'
    });

    res.json(result.map(d => ({
      date: d.date.toISOString().split('T')[0],
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
      volume: d.volume
    })));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = app;

if (require.main === module) {
  const PORT = 3001;
  app.listen(PORT, () => console.log(`API server running on port ${PORT}`));
}
```

- [ ] **Step 6: Run tests — verify they pass**

```bash
cd api && npm test
```

Expected: PASS — 2 test suites, 2 tests passed

- [ ] **Step 7: Commit**

```bash
git add api/package.json api/package-lock.json api/server.js api/server.test.js
git commit -m "feat: Node.js Express API for live and historical S&P 500 data"
```

---

## Task 3: SQLite Database Init (TDD)

**Files:**
- Create: `tests/test_init_db.py`
- Create: `db/init_db.py`

- [ ] **Step 1: Write failing test — `tests/test_init_db.py`**

```python
import sqlite3
import db.init_db as init_db_module

def test_creates_historical_prices_table(tmp_path):
    db_path = str(tmp_path / 'test.db')
    init_db_module.init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='historical_prices'"
    )
    assert cursor.fetchone() is not None
    conn.close()

def test_creates_predictions_table(tmp_path):
    db_path = str(tmp_path / 'test.db')
    init_db_module.init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'"
    )
    assert cursor.fetchone() is not None
    conn.close()

def test_historical_prices_columns(tmp_path):
    db_path = str(tmp_path / 'test.db')
    init_db_module.init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('PRAGMA table_info(historical_prices)')
    cols = {row[1] for row in cursor.fetchall()}
    assert cols == {'date', 'open', 'high', 'low', 'close', 'volume'}
    conn.close()
```

- [ ] **Step 2: Run test — verify it fails**

```bash
pytest tests/test_init_db.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'db.init_db'`

- [ ] **Step 3: Implement `db/init_db.py`**

```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'sp500.db')

def init_db(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            date    TEXT PRIMARY KEY,
            open    REAL,
            high    REAL,
            low     REAL,
            close   REAL,
            volume  INTEGER
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            run_date        TEXT,
            forecast_date   TEXT PRIMARY KEY,
            predicted_close REAL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialized at {path}")

if __name__ == '__main__':
    init_db()
```

- [ ] **Step 4: Create empty `db/__init__.py`**

```bash
touch db/__init__.py
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_init_db.py -v
```

Expected: PASS — 3 passed

- [ ] **Step 6: Run init to create the real DB**

```bash
python db/init_db.py
```

Expected: `Database initialized at db/sp500.db`

- [ ] **Step 7: Commit**

```bash
git add db/__init__.py db/init_db.py tests/test_init_db.py
git commit -m "feat: SQLite schema — historical_prices and predictions tables"
```

---

## Task 4: Data Sync Script (TDD)

**Files:**
- Create: `tests/test_sync_data.py`
- Create: `db/sync_data.py`

- [ ] **Step 1: Write failing test — `tests/test_sync_data.py`**

```python
import sqlite3
from unittest.mock import patch, MagicMock
import db.init_db as init_db_module
import db.sync_data as sync_module

SAMPLE_HISTORICAL = [
    {'date': '2024-01-02', 'open': 4742.83, 'high': 4763.13,
     'low': 4728.75, 'close': 4742.83, 'volume': 3500000000},
    {'date': '2024-01-03', 'open': 4700.00, 'high': 4720.00,
     'low': 4690.00, 'close': 4704.81, 'volume': 3200000000},
]

def test_sync_historical_inserts_rows(tmp_path):
    db_path = str(tmp_path / 'test.db')
    init_db_module.init_db(db_path)

    mock_resp = MagicMock()
    mock_resp.json.return_value = SAMPLE_HISTORICAL

    with patch('db.sync_data.requests.get', return_value=mock_resp):
        sync_module.sync_historical(db_path=db_path)

    conn = sqlite3.connect(db_path)
    count = conn.execute('SELECT COUNT(*) FROM historical_prices').fetchone()[0]
    conn.close()
    assert count == 2

def test_sync_historical_upserts_on_conflict(tmp_path):
    db_path = str(tmp_path / 'test.db')
    init_db_module.init_db(db_path)

    mock_resp = MagicMock()
    mock_resp.json.return_value = SAMPLE_HISTORICAL

    with patch('db.sync_data.requests.get', return_value=mock_resp):
        sync_module.sync_historical(db_path=db_path)
        sync_module.sync_historical(db_path=db_path)  # second call — no duplicates

    conn = sqlite3.connect(db_path)
    count = conn.execute('SELECT COUNT(*) FROM historical_prices').fetchone()[0]
    conn.close()
    assert count == 2
```

- [ ] **Step 2: Run test — verify it fails**

```bash
pytest tests/test_sync_data.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'db.sync_data'`

- [ ] **Step 3: Implement `db/sync_data.py`**

```python
import sqlite3
import requests
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'sp500.db')
API_BASE = 'http://localhost:3001/api'

def sync_historical(api_base=API_BASE, db_path=None):
    path = db_path or DB_PATH
    response = requests.get(f'{api_base}/historical')
    response.raise_for_status()
    data = response.json()

    conn = sqlite3.connect(path)
    conn.executemany(
        '''INSERT OR REPLACE INTO historical_prices
           (date, open, high, low, close, volume)
           VALUES (:date, :open, :high, :low, :close, :volume)''',
        data
    )
    conn.commit()
    conn.close()
    print(f"Synced {len(data)} historical records")

def get_live(api_base=API_BASE):
    response = requests.get(f'{api_base}/live')
    response.raise_for_status()
    data = response.json()
    print(f"Live: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
    return data

if __name__ == '__main__':
    sync_historical()
    get_live()
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_sync_data.py -v
```

Expected: PASS — 2 passed

- [ ] **Step 5: Commit**

```bash
git add db/sync_data.py tests/test_sync_data.py
git commit -m "feat: data sync — fetch historical and live S&P 500 from Node API into SQLite"
```

---

## Task 5: LSTM Training Script

**Files:**
- Create: `model/__init__.py`
- Create: `model/train.py`

*No TDD for training — we verify by running it and checking the output files exist.*

- [ ] **Step 1: Create `model/__init__.py`**

```bash
touch model/__init__.py
```

- [ ] **Step 2: Implement `model/train.py`**

```python
import sqlite3
import numpy as np
import pandas as pd
import pickle
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'sp500.db')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'sp500_model.h5')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'scaler.pkl')

LOOKBACK = 60
EPOCHS = 20
BATCH_SIZE = 32

def load_closes(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    df = pd.read_sql(
        'SELECT close FROM historical_prices ORDER BY date',
        conn
    )
    conn.close()
    return df['close'].values.reshape(-1, 1)

def create_sequences(scaled, lookback):
    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i - lookback:i, 0])
        y.append(scaled[i, 0])
    return np.array(X), np.array(y)

def build_model(lookback):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train(db_path=None, model_path=None, scaler_path=None):
    closes = load_closes(db_path)
    assert len(closes) >= LOOKBACK + 1, \
        f"Need at least {LOOKBACK + 1} rows in historical_prices, got {len(closes)}"

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(closes)

    X, y = create_sequences(scaled, LOOKBACK)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    model = build_model(LOOKBACK)
    model.fit(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE,
              validation_split=0.1, verbose=1)

    m_path = model_path or MODEL_PATH
    s_path = scaler_path or SCALER_PATH

    model.save(m_path)
    with open(s_path, 'wb') as f:
        pickle.dump(scaler, f)

    print(f"Model saved to {m_path}")
    print(f"Scaler saved to {s_path}")

if __name__ == '__main__':
    train()
```

- [ ] **Step 3: Sync real data first (Node.js API must be running)**

In one terminal:
```bash
cd api && node server.js
```

In another terminal:
```bash
python db/sync_data.py
```

Expected: `Synced ~1258 historical records`

- [ ] **Step 4: Train the model**

```bash
python model/train.py
```

Expected: 20 epochs of training output, then:
```
Model saved to model/sp500_model.h5
Scaler saved to model/scaler.pkl
```

Training takes 1–3 minutes on CPU.

- [ ] **Step 5: Verify output files exist**

```bash
ls model/sp500_model.h5 model/scaler.pkl
```

Expected: Both files listed.

- [ ] **Step 6: Commit**

```bash
git add model/__init__.py model/train.py
git commit -m "feat: LSTM training — 60-day lookback, 2 layers, 20 epochs, saves model + scaler"
```

---

## Task 6: LSTM Prediction Script (TDD)

**Files:**
- Create: `tests/test_predict.py`
- Create: `model/predict.py`

- [ ] **Step 1: Write failing test — `tests/test_predict.py`**

```python
import sqlite3
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import db.init_db as init_db_module
import model.predict as predict_module

def _seed_db(db_path, n=60):
    init_db_module.init_db(db_path)
    conn = sqlite3.connect(db_path)
    dates = [(date(2024, 1, 1) + timedelta(days=i)).isoformat() for i in range(n)]
    prices = np.linspace(4000, 5000, n).tolist()
    conn.executemany(
        'INSERT INTO historical_prices (date, open, high, low, close, volume) VALUES (?,?,?,?,?,?)',
        [(d, p, p, p, p, 1_000_000) for d, p in zip(dates, prices)]
    )
    conn.commit()
    conn.close()

def test_predict_writes_30_rows(tmp_path):
    db_path = str(tmp_path / 'test.db')
    _seed_db(db_path)

    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([[0.5]])

    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.ones((60, 1)) * 0.5
    mock_scaler.inverse_transform.return_value = np.ones((30, 1)) * 5000.0

    with patch('model.predict.load_model', return_value=mock_model), \
         patch('model.predict.pickle.load', return_value=mock_scaler), \
         patch('builtins.open', MagicMock()):
        predict_module.predict(db_path=db_path)

    conn = sqlite3.connect(db_path)
    count = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
    conn.close()
    assert count == 30

def test_predict_skips_weekends(tmp_path):
    db_path = str(tmp_path / 'test.db')
    _seed_db(db_path)

    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([[0.5]])
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.ones((60, 1)) * 0.5
    mock_scaler.inverse_transform.return_value = np.ones((30, 1)) * 5000.0

    with patch('model.predict.load_model', return_value=mock_model), \
         patch('model.predict.pickle.load', return_value=mock_scaler), \
         patch('builtins.open', MagicMock()):
        predict_module.predict(db_path=db_path)

    conn = sqlite3.connect(db_path)
    rows = conn.execute('SELECT forecast_date FROM predictions').fetchall()
    conn.close()
    for (d,) in rows:
        day_of_week = date.fromisoformat(d).weekday()
        assert day_of_week < 5, f"{d} is a weekend"
```

- [ ] **Step 2: Run test — verify it fails**

```bash
pytest tests/test_predict.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'model.predict'`

- [ ] **Step 3: Implement `model/predict.py`**

```python
import sqlite3
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'sp500.db')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'sp500_model.h5')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'scaler.pkl')

LOOKBACK = 60
FORECAST_DAYS = 30

def _load_recent_closes(db_path, n=LOOKBACK):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        f'SELECT close FROM historical_prices ORDER BY date DESC LIMIT {n}'
    ).fetchall()
    conn.close()
    closes = [r[0] for r in reversed(rows)]
    return np.array(closes).reshape(-1, 1)

def _next_trading_days(n):
    days = []
    current = datetime.today()
    while len(days) < n:
        current += timedelta(days=1)
        if current.weekday() < 5:
            days.append(current.strftime('%Y-%m-%d'))
    return days

def predict(db_path=None, model_path=None, scaler_path=None):
    db = db_path or DB_PATH
    m_path = model_path or MODEL_PATH
    s_path = scaler_path or SCALER_PATH

    model = load_model(m_path)
    with open(s_path, 'rb') as f:
        scaler = pickle.load(f)

    closes = _load_recent_closes(db)
    scaled = scaler.transform(closes)

    window = list(scaled[:, 0])
    raw_preds = []
    for _ in range(FORECAST_DAYS):
        x = np.array(window[-LOOKBACK:]).reshape(1, LOOKBACK, 1)
        p = model.predict(x, verbose=0)[0, 0]
        raw_preds.append(p)
        window.append(p)

    prices = scaler.inverse_transform(
        np.array(raw_preds).reshape(-1, 1)
    )[:, 0]

    run_date = datetime.today().strftime('%Y-%m-%d')
    forecast_dates = _next_trading_days(FORECAST_DAYS)

    conn = sqlite3.connect(db)
    conn.execute('DELETE FROM predictions WHERE run_date = ?', (run_date,))
    conn.executemany(
        'INSERT OR REPLACE INTO predictions (run_date, forecast_date, predicted_close) VALUES (?,?,?)',
        [(run_date, d, float(p)) for d, p in zip(forecast_dates, prices)]
    )
    conn.commit()
    conn.close()
    print(f"Generated {FORECAST_DAYS} predictions starting {forecast_dates[0]}")

if __name__ == '__main__':
    predict()
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_predict.py -v
```

Expected: PASS — 2 passed

- [ ] **Step 5: Run predict against real data**

```bash
python model/predict.py
```

Expected: `Generated 30 predictions starting <next weekday>`

- [ ] **Step 6: Commit**

```bash
git add model/predict.py tests/test_predict.py
git commit -m "feat: LSTM prediction — 30-day forecast written to SQLite predictions table"
```

---

## Task 7: Chart Helpers (TDD)

**Files:**
- Create: `tests/test_charts.py`
- Create: `dashboard/__init__.py`
- Create: `dashboard/charts.py`

- [ ] **Step 1: Write failing test — `tests/test_charts.py`**

```python
import pandas as pd
import plotly.graph_objects as go
from dashboard.charts import build_historical_chart, build_forecast_chart

def _historical_df():
    return pd.DataFrame({
        'date': ['2024-01-02', '2024-01-03', '2024-01-04'],
        'close': [4742.83, 4704.81, 4697.24]
    })

def _pred_df():
    return pd.DataFrame({
        'forecast_date': ['2024-01-05', '2024-01-08'],
        'predicted_close': [4710.0, 4725.0]
    })

def test_build_historical_chart_returns_figure():
    fig = build_historical_chart(_historical_df())
    assert isinstance(fig, go.Figure)

def test_build_historical_chart_has_one_trace():
    fig = build_historical_chart(_historical_df())
    assert len(fig.data) == 1

def test_build_historical_chart_trace_is_blue():
    fig = build_historical_chart(_historical_df())
    assert fig.data[0].line.color == '#4a9eff'

def test_build_forecast_chart_returns_figure():
    fig = build_forecast_chart(_historical_df(), _pred_df())
    assert isinstance(fig, go.Figure)

def test_build_forecast_chart_has_two_traces():
    fig = build_forecast_chart(_historical_df(), _pred_df())
    assert len(fig.data) == 2

def test_build_forecast_chart_trace_names():
    fig = build_forecast_chart(_historical_df(), _pred_df())
    names = {t.name for t in fig.data}
    assert names == {'Actual', 'Forecast'}
```

- [ ] **Step 2: Run test — verify it fails**

```bash
pytest tests/test_charts.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'dashboard.charts'`

- [ ] **Step 3: Create `dashboard/__init__.py`**

```bash
touch dashboard/__init__.py
```

- [ ] **Step 4: Implement `dashboard/charts.py`**

```python
import pandas as pd
import plotly.graph_objects as go

def build_historical_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['close'],
        mode='lines', name='S&P 500',
        line=dict(color='#4a9eff', width=2)
    ))
    fig.update_layout(
        xaxis_title='Date', yaxis_title='Price (USD)',
        plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    return fig

def build_forecast_chart(actual_df: pd.DataFrame, pred_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual_df['date'], y=actual_df['close'],
        mode='lines', name='Actual',
        line=dict(color='#4a9eff', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=pred_df['forecast_date'], y=pred_df['predicted_close'],
        mode='lines', name='Forecast',
        line=dict(color='#ff884a', width=2, dash='dot')
    ))
    fig.update_layout(
        xaxis_title='Date', yaxis_title='Price (USD)',
        plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
        font=dict(color='white'),
        legend=dict(orientation='h', y=1.1),
        margin=dict(l=0, r=0, t=20, b=0)
    )
    return fig
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_charts.py -v
```

Expected: PASS — 6 passed

- [ ] **Step 6: Commit**

```bash
git add dashboard/__init__.py dashboard/charts.py tests/test_charts.py
git commit -m "feat: chart helpers — build_historical_chart and build_forecast_chart"
```

---

## Task 8: Streamlit Dashboard

**Files:**
- Create: `dashboard/app.py`

*Streamlit UI cannot be unit-tested — verified by running it.*

- [ ] **Step 1: Implement `dashboard/app.py`**

```python
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

# Live price header
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

# Side-by-side layout
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
        actual = get_historical(30)
        st.plotly_chart(build_forecast_chart(actual, preds), use_container_width=True)
        st.caption('Blue = actual · Orange dashed = LSTM prediction')
    else:
        st.info('No predictions — run: python model/predict.py')

st.caption(f"Live price refreshes every 60s · Last loaded: {datetime.now().strftime('%H:%M:%S')}")
```

- [ ] **Step 2: Run the dashboard (Node.js API must be running)**

Terminal 1:
```bash
cd api && node server.js
```

Terminal 2:
```bash
streamlit run dashboard/app.py
```

Expected: Browser opens at `http://localhost:8501` showing live price, historical chart, and forecast chart side-by-side.

- [ ] **Step 3: Verify the golden path**

Check all of these in the browser:
- [ ] Live price header shows a real number with ▲/▼ and green/red color
- [ ] Historical chart renders with blue line for the selected range
- [ ] Time range buttons (1M / 3M / 1Y / 5Y) switch the chart correctly
- [ ] Forecast chart shows blue actual line + orange dashed predicted line
- [ ] Caption reads "Blue = actual · Orange dashed = LSTM prediction"

- [ ] **Step 4: Commit**

```bash
git add dashboard/app.py
git commit -m "feat: Streamlit dashboard — side-by-side historical chart and 30-day forecast"
```

---

## Task 9: Full Test Suite

- [ ] **Step 1: Run all Python tests**

```bash
pytest tests/ -v
```

Expected:
```
tests/test_init_db.py::test_creates_historical_prices_table PASSED
tests/test_init_db.py::test_creates_predictions_table PASSED
tests/test_init_db.py::test_historical_prices_columns PASSED
tests/test_sync_data.py::test_sync_historical_inserts_rows PASSED
tests/test_sync_data.py::test_sync_historical_upserts_on_conflict PASSED
tests/test_predict.py::test_predict_writes_30_rows PASSED
tests/test_predict.py::test_predict_skips_weekends PASSED
tests/test_charts.py::test_build_historical_chart_returns_figure PASSED
tests/test_charts.py::test_build_historical_chart_has_one_trace PASSED
tests/test_charts.py::test_build_historical_chart_trace_is_blue PASSED
tests/test_charts.py::test_build_forecast_chart_returns_figure PASSED
tests/test_charts.py::test_build_forecast_chart_has_two_traces PASSED
tests/test_charts.py::test_build_forecast_chart_trace_names PASSED
13 passed
```

- [ ] **Step 2: Run Node.js tests**

```bash
cd api && npm test
```

Expected: 2 passed

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "chore: all tests passing — 13 Python + 2 Node.js"
```

---

## Running the Completed Project

```bash
# Terminal 1 — start the data API
cd api && node server.js

# Terminal 2 — sync data + train + predict (first time only)
python db/sync_data.py
python model/train.py       # takes 1-3 min
python model/predict.py

# Terminal 2 — launch dashboard
streamlit run dashboard/app.py
```

Open `http://localhost:8501`
