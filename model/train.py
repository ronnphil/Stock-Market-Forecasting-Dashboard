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
