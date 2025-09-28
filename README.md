# Laundry Planner 🌦️

Laundry Planner is a full-stack weather-driven application that predicts whether it’s safe to dry laundry outdoors tomorrow.  
It combines **FastAPI backend**, **React frontend**, and **machine learning models** (Prophet / XGBoost / optional LSTM) to provide predictions and useful weather features.

---

## 📁 Project Structure
```text
├── .venv/                           # Python virtual environment (not tracked by git)
├── backend/                         # FastAPI backend (API endpoints + model loading)
│   ├── app/
│   │   ├── main.py                  # Entry point for FastAPI
│   │   ├── api.py                   # Endpoints for rule-based, Prophet, XGBoost predictions
│   │   ├── config.py                # Environment variables and settings
│   │   ├── utils.py                 # OpenWeather fetch + rainfall calculation
│   │   └── models/                  # Trained models (prophet_model.joblib, xgb_model.joblib, lstm_model.h5)
│   └── requirements.txt             # Python dependencies for backend
├── data/                            # Datasets (forecast + processed)
│   ├── forecast_London.csv
│   └── world_cities.json
├── data_pipeline/                   # Scripts to fetch and preprocess weather data
│   ├── fetch_openweather.py         # Fetch 5-day forecast from OpenWeather API
│   ├── preprocess.py                # Daily aggregation of forecast data
│   ├── update_dataset.py            # Append new data to existing dataset
│   └── .env                         # Contains OPENWEATHER_KEY (never commit)
├── frontend/                        # React (Vite) frontend
│   ├── src/                         # UI components, charts, and API client
│   ├── package.json
│   └── vite.config.js
├── training/                        # Training scripts for ML models
│   ├── features.py                  # Feature engineering for models
│   ├── train_prophet.py             # Train Prophet model
│   ├── train_xgboost.py             # Train XGBoost model
│   └── train_lstm.py                # Train optional LSTM model
└── README.md                        # This file
```

---

## 🚀 Features

- **Rule-based prediction** — checks if tomorrow’s rain ≤ threshold.
- **Prophet model** — forecasts rainfall trend.
- **XGBoost model** — predicts rainfall using engineered features.
- **Optional LSTM model** — deep learning time-series approach.
- **React frontend** — allows city search, displays prediction cards, and weather features.
- **OpenWeather API integration** — automatically fetches weather data.

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/JJ-UNIVERZe/LaundryPlanner.git
cd LaundryPlanner
```
2. Backend (FastAPI)

Create and activate virtual environment:
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate
# macOS/Linux:
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r backend/app/requirements.txt
```

Configure your OpenWeather API key:

# Inside data_pipeline/.env

OPENWEATHER_KEY=YOUR_OPENWEATHER_API_KEY


Run backend:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
3. Frontend (React)

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Frontend available at:
```bash
➡️ http://localhost:3000
```

4. Data Pipeline (Optional for training)

Fetch weather forecast:
```
cd data_pipeline
python fetch_openweather.py --city London
```

Aggregate to daily data:
```bash
import pandas as pd
from preprocess import daily_aggregate

df = pd.read_csv("../data/forecast_London.csv")
daily = daily_aggregate(df)
daily.to_csv("../data/daily_London.csv", index=False)
```
5. Train Models

Train Prophet:
```bash
cd training
python train_prophet.py --data ../data/daily_London.csv
```

Train XGBoost:
```bash
python train_xgboost.py --data ../data/daily_London.csv
```

Optional LSTM:
```bash
python train_lstm.py --data ../data/daily_London.csv
```
📝 Environment Variables

Create data_pipeline/.env:

  OPENWEATHER_KEY=YOUR_OPENWEATHER_API_KEY

🖥️ Technologies Used

  FastAPI (Python backend)
  
  React + Vite (Frontend UI)
  
  Prophet, XGBoost, TensorFlow/Keras (ML Models)
  
  OpenWeather API (Weather data)
  
  Joblib (Model persistence)
