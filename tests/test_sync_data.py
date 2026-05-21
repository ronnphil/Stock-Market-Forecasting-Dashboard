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
