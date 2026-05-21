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
