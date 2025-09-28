import requests
import pandas as pd
import datetime
import time

API_KEY = "b7b2d75c27ec7e01bb92097b1bee39ee"
BASE = "http://api.openweathermap.org/data/2.5/forecast"


def fetch_city(city, save_csv=True, outpath="../data/forecast_{city}.csv"):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    r = requests.get(BASE, params=params)
    r.raise_for_status()
    j = r.json()
    rows = []
    for item in j.get("list", []):
        dt = datetime.datetime.fromtimestamp(item["dt"]) 
        rows.append({
            "dt": dt,
            "temp": item.get("main", {}).get("temp"),
            "humidity": item.get("main", {}).get("humidity"),
            "rain_3h": item.get("rain", {}).get("3h", 0.0),
            "pressure": item.get("main", {}).get("pressure"),
            "wind_speed": item.get("wind", {}).get("speed"),
        })
    df = pd.DataFrame(rows)
    if save_csv:
        df.to_csv(outpath.format(city=city), index=False)
    return df


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--city", default="London")
    args = p.parse_args()
    df = fetch_city(args.city, save_csv=True, outpath="../data/forecast_{city}.csv")
    print(df.head())