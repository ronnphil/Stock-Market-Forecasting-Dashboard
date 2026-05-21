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
