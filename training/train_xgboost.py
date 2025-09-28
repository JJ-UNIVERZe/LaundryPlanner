import joblib
import xgboost as xgb
import pandas as pd
from features import build_features
import argparse
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
  
parser = argparse.ArgumentParser()
parser.add_argument('--data', required=True)
parser.add_argument('--out', default='../backend/app/models/xgb_model.joblib')
args = parser.parse_args()

daily = pd.read_csv(args.data)
X_train, X_test, y_train, y_test = build_features(daily)
model = xgb.XGBRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)
joblib.dump(model, args.out)
print('Saved XGBoost model to', args.out)

pred = model.predict(X_test)
print('MAE:', mean_absolute_error(y_test, pred))
print('RMSE:', np.sqrt(mean_squared_error(y_test, pred)))
