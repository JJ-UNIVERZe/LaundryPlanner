import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import argparse
import os

# -----------------------------
# Parse arguments
# -----------------------------
parser = argparse.ArgumentParser(description="Train an LSTM model on daily rainfall data")
parser.add_argument('--data', required=True, help="Path to daily CSV (with columns: date,rain_mm,...)")
parser.add_argument('--out', default='../backend/app/models/lstm_model.h5', help="Path to save trained model")
parser.add_argument('--window', type=int, default=14, help="Number of days in input sequence window")
args = parser.parse_args()

# -----------------------------
# Load and prepare data
# -----------------------------
df = pd.read_csv(args.data)

series = df['rain_mm'].values.astype(float)

window = args.window
X, y = [], []

for i in range(window, len(series)):
    X.append(series[i-window:i])
    y.append(series[i])

if len(X) == 0:
    raise ValueError(
        f"Not enough data to create sequences with window={window}. "
        f"Need at least {window+1} rows in your CSV."
    )

X = np.array(X).reshape(len(X), window, 1)
y = np.array(y)

split = int(0.8 * len(X))
Xtr, Xv = X[:split], X[split:]
ytr, yv = y[:split], y[split:]

# -----------------------------
# Build LSTM model
# -----------------------------
model = Sequential([
    LSTM(64, input_shape=(window, 1)),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')

# -----------------------------
# Train with early stopping
# -----------------------------
es = EarlyStopping(patience=10, restore_best_weights=True)
model.fit(Xtr, ytr, validation_data=(Xv, yv), epochs=200, batch_size=16, callbacks=[es])

# -----------------------------
# Save the model
# -----------------------------
os.makedirs(os.path.dirname(args.out), exist_ok=True)
model.save(args.out)
print(f"✅ Saved LSTM model to {args.out}")
