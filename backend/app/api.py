from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
import joblib
import numpy as np
import json
from .utils import fetch_5day_forecast, sum_tomorrow_rain
from .config import settings
import os

router = APIRouter()

# Load models lazily
BASE_DIR = os.path.dirname(__file__)
PROP_PATH = os.path.join(BASE_DIR, "models", "prophet_model.joblib")
XGB_PATH = os.path.join(BASE_DIR, "models", "xgb_model.joblib")
LSTM_PATH = os.path.join(BASE_DIR, "models", "lstm_model.h5")


def load_model(path):
    if os.path.exists(path):
        return joblib.load(path)
    return None


class CityRequest(BaseModel):
    city: str | None = None
    lat: float | None = None
    lon: float | None = None


@router.post("/predict/rule")
async def predict_rule(payload: CityRequest):
    try:
        city = (payload.city or "").strip()
        if "," in city:
            city = city.split(",")[0].strip()
        if not city and (payload.lat is None or payload.lon is None):
            raise HTTPException(status_code=422, detail="City or lat/lon required")
        f = fetch_5day_forecast(city if city else None, payload.lat, payload.lon)
        total = sum_tomorrow_rain(f)
        safe = total <= settings.RAIN_THRESHOLD_MM
        meta_city = f.get("city", {}).get("name") or city
        return {"city": meta_city, "tomorrow_rain_mm": total, "safe_to_dry_outside": safe}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/predict/prophet")
async def predict_prophet(payload: CityRequest):
    model = load_model(PROP_PATH)
    if not model:
        raise HTTPException(status_code=404, detail="Prophet model not found. Train first.")

    city = (payload.city or "").strip()
    if "," in city:
        city = city.split(",")[0].strip()
    if not city and (payload.lat is None or payload.lon is None):
        raise HTTPException(status_code=422, detail="City or lat/lon required")
    f = fetch_5day_forecast(city if city else None, payload.lat, payload.lon)
    total = sum_tomorrow_rain(f)
    pred = model.predict_total_from_baseline(total) if hasattr(model, "predict_total_from_baseline") else float(total)
    safe = pred <= settings.RAIN_THRESHOLD_MM
    meta_city = f.get("city", {}).get("name") or city
    return {"city": meta_city, "predicted_rain_mm": pred, "safe_to_dry_outside": safe}


@router.post("/predict/xgboost")
async def predict_xgboost(payload: CityRequest):
    model = load_model(XGB_PATH)
    if not model:
        raise HTTPException(status_code=404, detail="XGBoost model not found. Train first.")
    city = (payload.city or "").strip()
    if "," in city:
        city = city.split(",")[0].strip()
    if not city and (payload.lat is None or payload.lon is None):
        raise HTTPException(status_code=422, detail="City or lat/lon required")
    # Build feature vector to match training order: [temp, humidity, wind_speed, rain_lag_1, dayofyear]
    f = fetch_5day_forecast(city if city else None, payload.lat, payload.lon)
    temps = []
    hums = []
    winds = []
    import datetime
    today = datetime.date.today()
    tomorrow_date = today + datetime.timedelta(days=1)
    # Aggregate for tomorrow
    for item in f.get("list", []):
        ts = datetime.datetime.fromtimestamp(item["dt"]) 
        if ts.date() == tomorrow_date:
            temps.append(item.get("main", {}).get("temp") or 0.0)
            hums.append(item.get("main", {}).get("humidity") or 0.0)
            winds.append(item.get("wind", {}).get("speed") or 0.0)
    temp_mean = float(np.mean(temps)) if temps else 0.0
    hum_mean = float(np.mean(hums)) if hums else 0.0
    wind_mean = float(np.mean(winds)) if winds else 0.0
    # Approximate lag-1 using today's total rain from forecast (fallback to 0.0)
    today_total = 0.0
    for item in f.get("list", []):
        ts = datetime.datetime.fromtimestamp(item["dt"]) 
        if ts.date() == today:
            today_total += item.get("rain", {}).get("3h", 0.0)
    rain_lag_1 = float(today_total)
    dayofyear = float(tomorrow_date.timetuple().tm_yday)

    feat = np.array([[temp_mean, hum_mean, wind_mean, rain_lag_1, dayofyear]], dtype=float)
    pred = float(model.predict(feat)[0])
    safe = pred <= settings.RAIN_THRESHOLD_MM
    meta_city = f.get("city", {}).get("name") or city
    return {"city": meta_city, "predicted_rain_mm": pred, "safe_to_dry_outside": safe}


@router.get("/evaluate")
async def evaluate_models():
    """Evaluate available models on held-out split of daily_London.csv.
    Returns MAE and RMSE for baseline rule and XGBoost (if available).
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import numpy as np
    import datetime

    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "daily_London.csv")
    data_path = os.path.normpath(data_path)
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="daily_London.csv not found")

    df = pd.read_csv(data_path)
    if "date" not in df.columns or "rain_mm" not in df.columns:
        raise HTTPException(status_code=400, detail="daily_London.csv missing required columns")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").copy()
    # Simple features similar to training
    df["rain_lag_1"] = df["rain_mm"].shift(1)
    df["dayofyear"] = df["date"].dt.dayofyear
    df = df.dropna().reset_index(drop=True)
    if len(df) < 20:
        raise HTTPException(status_code=400, detail="Not enough data to evaluate")
    X = df[[c for c in df.columns if c not in ["date", "rain_mm"]]]
    y = df["rain_mm"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    results = {}
    # Baseline rule: predict mean of yesterday rain (lag1)
    baseline_pred = X_test["rain_lag_1"].fillna(y_train.mean())
    results["rule"] = {
        "MAE": float(mean_absolute_error(y_test, baseline_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_test, baseline_pred))),
    }

    # XGBoost if available
    xgb_model = load_model(XGB_PATH)
    if xgb_model is not None:
        try:
            xgb_pred = xgb_model.predict(X_test)
            results["xgboost"] = {
                "MAE": float(mean_absolute_error(y_test, xgb_pred)),
                "RMSE": float(np.sqrt(mean_squared_error(y_test, xgb_pred))),
            }
        except Exception as e:
            results["xgboost"] = {"error": str(e)}
    else:
        results["xgboost"] = {"error": "model not found"}

    # Choose best by MAE
    def best_model(res):
        best = None
        best_mae = None
        for name, metrics in res.items():
            if "MAE" in metrics:
                if best is None or metrics["MAE"] < best_mae:
                    best = name
                    best_mae = metrics["MAE"]
        return best, best_mae

    best, best_mae = best_model(results)
    return {"results": results, "best": best, "best_mae": best_mae}


@router.post("/upload/model/{model_name}")
async def upload_model(model_name: str, file: UploadFile = File(...)):
    # Accept zipped or joblib file and store in models/
    dest = os.path.join(BASE_DIR, "models", model_name)
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)
    return {"ok": True, "saved_to": dest}


@router.post("/features")
async def compute_features(payload: CityRequest):
    """Return input features used by models plus location metadata from OpenWeather."""
    try:
        city = (payload.city or "").strip()
        if "," in city:
            city = city.split(",")[0].strip()
        if not city and (payload.lat is None or payload.lon is None):
            raise HTTPException(status_code=422, detail="City or lat/lon required")
        f = fetch_5day_forecast(city if city else None, payload.lat, payload.lon)
        # Location metadata
        meta = f.get("city", {})
        coord = meta.get("coord", {})
        country = meta.get("country")

        import datetime
        temps = []
        hums = []
        winds = []
        today = datetime.date.today()
        tomorrow_date = today + datetime.timedelta(days=1)
        # Aggregate for tomorrow day window
        for item in f.get("list", []):
            ts = datetime.datetime.fromtimestamp(item["dt"]) 
            if ts.date() == tomorrow_date:
                temps.append(item.get("main", {}).get("temp") or 0.0)
                hums.append(item.get("main", {}).get("humidity") or 0.0)
                winds.append(item.get("wind", {}).get("speed") or 0.0)
        temp_mean = float(np.mean(temps)) if temps else 0.0
        hum_mean = float(np.mean(hums)) if hums else 0.0
        wind_mean = float(np.mean(winds)) if winds else 0.0
        # Rain lag-1 approximation: total rain today from forecast
        today_total = 0.0
        for item in f.get("list", []):
            ts = datetime.datetime.fromtimestamp(item["dt"]) 
            if ts.date() == today:
                today_total += item.get("rain", {}).get("3h", 0.0)
        rain_lag_1 = float(today_total)
        dayofyear = float(tomorrow_date.timetuple().tm_yday)

        return {
            "city": meta.get("name") or city,
            "country": country,
            "lat": coord.get("lat"),
            "lon": coord.get("lon"),
            "features": {
                "temp_mean_tomorrow": temp_mean,
                "humidity_mean_tomorrow": hum_mean,
                "wind_speed_mean_tomorrow": wind_mean,
                "rain_lag_1": rain_lag_1,
                "dayofyear_tomorrow": dayofyear,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))