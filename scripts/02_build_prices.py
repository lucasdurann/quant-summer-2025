import pandas as pd
import yfinance as yf
from pathlib import Path

TICKERS = ["CRESY", "IRS", "SPY"]
START, END = "2015-01-01", "2025-06-01"
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # jumps out of scripts/data/
DATA_DIR = PROJECT_ROOT / "data" / "raw_yfinance"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTFILE = DATA_DIR / "prices_arg.parquet"

def fetch_prices(tickers, start, end):
    """Download Adj Close prices from Yahoo."""
    df = (
        yf.download(tickers, start=start, end=end, progress=False)["Close"]
        .rename_axis("date")
        .asfreq("B")                 # business-day frequency
        .ffill(limit=1)              # fill 1-day gaps only
    )
    return df

def sanity_checks(df):
    """Quick quality gates before saving."""
    # 1. Missing data audit
    na_pct = df.isna().mean() * 100
    assert (na_pct < 0.5).all(), f"Too many NaNs:\n{na_pct}"
    
    # 2. Abnormal jumps flag
    rets = df.pct_change()
    spikes = (rets.abs() > 5).sum()
    if spikes.any():
        print("⚠️ spikes >500 % days:\n", spikes[spikes > 0])

prices = fetch_prices(TICKERS, START, END)
sanity_checks(prices)

# Save as parquet (gzip compression by default)
prices.to_parquet(OUTFILE)
print(f"✅ Saved {OUTFILE.relative_to(Path.cwd())} | shape = {prices.shape}")
