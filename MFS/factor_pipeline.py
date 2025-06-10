#!/usr/bin/env python
"""
factor_pipeline.py  – Minimal 3-factor pipeline for 30 stocks
"""
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import yfinance as yf
from scipy import stats

# --------------------------------------------------
# 1. Config
# --------------------------------------------------
TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "UNH", "JPM", "V",
    "PG", "JNJ", "HD", "MA", "XOM", "CVX", "KO", "PEP", "MCD", "BAC",
    "CSCO", "IBM", "CRM", "ORCL", "WMT", "COST", "T", "DIS", "NKE", "INTC"
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

# Assemble
factors = pd.DataFrame({
    "value_raw": value_raw,
    "momentum_raw": momentum_raw,
    "quality_raw": quality_raw
})

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