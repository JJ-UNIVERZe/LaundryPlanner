import pandas as pd
from prophet import Prophet
import joblib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data', required=True)  # path to daily csv
parser.add_argument('--out', default='../backend/app/models/prophet_model.joblib')
args = parser.parse_args()

# Load and format
raw = pd.read_csv(args.data)
raw['date'] = pd.to_datetime(raw['date'])
df = raw[['date', 'rain_mm']].rename(columns={'date': 'ds', 'rain_mm': 'y'})

m = Prophet()
m.fit(df)
joblib.dump(m, args.out)
print('Saved Prophet model to', args.out)
