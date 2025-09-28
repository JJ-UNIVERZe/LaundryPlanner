import pandas as pd
from preprocess import daily_aggregate
import subprocess
import sys

city = sys.argv[1] if len(sys.argv) > 1 else "London"

# 1. Fetch the latest forecast (runs your existing script)
subprocess.run([sys.executable, "fetch_openweather.py", "--city", city], check=True)

# 2. Read the forecast CSV just created
forecast_path = f"../data/forecast_{city}.csv"
df_new = pd.read_csv(forecast_path)
daily_new = daily_aggregate(df_new)

# 3. Append or create the daily file
daily_path = f"../data/daily_{city}.csv"
try:
    old = pd.read_csv(daily_path)
except FileNotFoundError:
    old = pd.DataFrame(columns=daily_new.columns)

combined = pd.concat([old, daily_new], ignore_index=True)
combined = combined.drop_duplicates(subset='date').sort_values('date')
combined.to_csv(daily_path, index=False)

print(f"Updated dataset saved to {daily_path}")
