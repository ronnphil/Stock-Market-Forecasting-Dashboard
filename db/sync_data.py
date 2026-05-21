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
