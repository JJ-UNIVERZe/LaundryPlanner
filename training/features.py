import pandas as pd
from sklearn.model_selection import train_test_split

def build_features(daily_df):
    df = daily_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    for l in [1]:  # only one lag because data is small
        df[f'rain_lag_{l}'] = df['rain_mm'].shift(l)
    df['dayofyear'] = df['date'].dt.dayofyear
    df = df.dropna()
    X = df[[c for c in df.columns if c not in ['date', 'rain_mm']]]
    y = df['rain_mm']
    return train_test_split(X, y, test_size=0.2, random_state=42)
