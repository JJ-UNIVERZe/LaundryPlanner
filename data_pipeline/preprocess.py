import pandas as pd
import numpy as np


def daily_aggregate(forecast_df):
    df = forecast_df.copy()
    df['date'] = pd.to_datetime(df['dt']).dt.date
    daily = df.groupby('date').agg({
        'rain_3h': 'sum',
        'temp': 'mean',
        'humidity': 'mean',
        'wind_speed': 'mean'
    }).reset_index().rename(columns={'rain_3h': 'rain_mm'})
    return daily


def add_lags(df, target_col='rain_mm', lags=[1,2,3,7]):
    out = df.copy()
    for l in lags:
        out[f'{target_col}_lag_{l}'] = out[target_col].shift(l)
    out = out.dropna().reset_index(drop=True)
    return out