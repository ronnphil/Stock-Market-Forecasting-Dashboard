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
