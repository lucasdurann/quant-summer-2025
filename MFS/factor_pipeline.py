#!/usr/bin/env python
"""
factor_pipeline.py  – Minimal 3-factor pipeline for 30 stocks
"""
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import yfinance as yf
import scipy as sp
from scipy import stats
from utils import forecast_vol  # Ensure utils.py is in the same directory or adjust import accordingly

# --------------------------------------------------
# 1. Config
# --------------------------------------------------
TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "UNH", "JPM", "V",
    "PG", "JNJ", "HD", "MA", "XOM", "CVX", "KO", "PEP", "MCD", "BAC",
    "CSCO", "IBM", "CRM", "ORCL", "WMT", "COST", "T", "DIS", "NKE", "SPY"
]  # → adjust any time

OUTPUT_DIR = Path("MFS/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOT = OUTPUT_DIR / f"factors_snapshot_{date.today():%Y%m%d}.csv"

# --------------------------------------------------
# 2. Download raw data
# --------------------------------------------------
print("Fetching price history…")
prices = yf.download(
    TICKERS,
    start=(date.today() - timedelta(days=400)),
    end=date.today(),
    auto_adjust=True,
    progress=False
)["Close"]

print("Fetching key data (slow but only once per ticker)…")
info = {t: yf.Ticker(t).info for t in TICKERS}

# Build helper DataFrame
meta = pd.DataFrame.from_dict(info, orient="index")

# ------------------------------------------------------------
# 2-b. Compute σ forecast (GARCH) and derive vol_cap
# ------------------------------------------------------------
print("Fitting GARCH per ticker …")

sigma_next = {}
for ticker in prices.columns:
    # forecast_vol returns a full σ series; take the last element
    sigma_series = forecast_vol(prices[ticker])
    sigma_next[ticker] = sigma_series.iloc[-1]

sigma_next = pd.Series(sigma_next, name="sigma_1d")  # index = tickers

# Basic risk-parity weight: inverse of σ
vol_cap = 1 / sigma_next
vol_cap.name = "vol_cap_raw"

# --------------------------------------------------
# 3. Raw factor metrics
# --------------------------------------------------
# Value  = 1 / Price-to-Sales (TTM)
ps = meta["priceToSalesTrailing12Months"]
value_raw = 1 / ps

# Momentum = 12-month total return
momentum_raw = prices.pct_change(252).iloc[-1]

# Quality  = 3-yr average ROE  (use .info -> 'returnOnEquity', already TTM;
# here we proxy with that single value for simplicity)
quality_raw = meta["returnOnEquity"]

extra_cols = pd.DataFrame({
    "vol_cap": vol_cap
})

# Assemble
factors = pd.DataFrame({
    "value_raw": value_raw,
    "momentum_raw": momentum_raw,
    "quality_raw": quality_raw
}).join(extra_cols)

# --------------------------------------------------
# 4. Z-score within universe
# --------------------------------------------------
for col in factors.columns:
    factors[col.replace("_raw", "")] = stats.zscore(factors[col].fillna(factors[col].median()))

# --------------------------------------------------
# 5. Composite rank
# --------------------------------------------------
factors["composite"] = factors[["value", "momentum", "quality"]].mean(axis=1)
factors = factors.sort_values("composite", ascending=False)

# --------------------------------------------------
# 6. Export snapshot
# --------------------------------------------------
factors.reset_index().rename(columns={"index": "ticker"}).to_csv(SNAPSHOT, index=False)
print("Saved snapshot →", SNAPSHOT.resolve())

# Optional preview
print(factors.head(10))
print("value_raw: the lower the better; momentum_raw: the higher the better; quality_raw: the higher the better; value, momentum, quality: z-scores; composite: mean of z-scores, the higher the better")