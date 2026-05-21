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
