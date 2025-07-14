import pandas as pd, numpy as np, pathlib

prices = pd.read_parquet("data/raw_yfinance/prices_arg.parquet")["IRS"]
rets   = 100 * np.log(prices).diff().dropna()          # % log-returns
rets = rets[rets != 0]
rets.to_csv("SaaSV/docs/IRS_returns_2015-25.csv", header=["IRSrtn"])
