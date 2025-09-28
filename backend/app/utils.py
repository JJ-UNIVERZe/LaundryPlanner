import requests
import datetime
from .config import settings

BASE_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"


def fetch_5day_forecast(city: str = None, lat: float = None, lon: float = None, api_key: str = None):
    key = api_key or settings.OPENWEATHER_KEY
    params = {"appid": key, "units": "metric"}
    if city:
        params["q"] = city
    else:
        params["lat"] = lat
        params["lon"] = lon
    r = requests.get(BASE_FORECAST_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def sum_tomorrow_rain(forecast_json, tz_offset_hours=0):
    # Sum rain (3h) for tomorrow local date
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    total = 0.0
    for item in forecast_json.get("list", []):
        ts = datetime.datetime.fromtimestamp(item["dt"]) + datetime.timedelta(hours=tz_offset_hours)
        if ts.date() == tomorrow:
            total += item.get("rain", {}).get("3h", 0.0)
    return total