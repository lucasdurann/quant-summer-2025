import sys, os
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import utils as ut
from utils import calc_spread_slippage

def sample_prices_constant_return(n_days: int = 260, daily_pct: float = 0.01) -> pd.Series:
    """ 
    Creat a Series of length n_days where each day's return is exactly daily_pct.
    Starting at price = 1.0 for simplicity:
    P_t = (1.0 + daily_pct) ** t
    """
    base = 1.0 + daily_pct
    # np.logspace isn't quite right here, so do cumprod manually:
    data = pd.Series([1.0]+[(1.0+daily_pct) for _ in range (n_days -1)])
    return data.cumprod().reset_index(drop=True)

def test_vol_constant_returns():
    # 260 days of constant returns at 1% daily
    p = sample_prices_constant_return()
    # Compute rolling_vol with a small window = 20
    vol_ts = ut.rolling_vol(p, window=20)

    # In the first 19 days: vol is NaN; from day 20 onward: vol == 0
    # Drop NaNs to only compare the non-NaN portion
    vol_non_na = vol_ts.dropna().values

    # Every element should be exactly 0.0
    assert np.allclose(vol_non_na, 0.0, atol=1e-10)

def test_sharpe_constant_returns_no_crash():
    p = sample_prices_constant_return()
    # Use rf=0.0 for simplicity, window=20 as before
    sr_ts = ut.rolling_sharpe(p, rf=0.0, window=20)

    # Drop the initial NaNs, then check remaining values:
    sr_non_na = sr_ts.dropna().values

    # None of the entries should be some random number; 
    # they should be either np.inf or np.nan. We check that
    # every value either is infinite or NaN.
    for val in sr_non_na:
        assert np.isinf(val) or np.isnan(val)

def test_vol_manual_small_series():
    # Example: prices = [100, 101, 102, 103, 102, 101, 100]
    # Compute daily returns by hand and compare rolling std for window=3
    prices = pd.Series([100, 101, 102, 103, 102, 101, 100], dtype=float)
    # Manually compute the first few rolling vols:
    # day 2 (index=2) window=3: returns = [1%, 0.9901%, 0.9804%], etc.
    # Rather than doing it by hand, we can compare against pandas directly:
    expected_std = prices.pct_change().rolling(window=3).std() * np.sqrt(252)

    output_vol = ut.rolling_vol(prices, window=3)
    # Compare elementwise (they should match exactly)
    pd.testing.assert_series_equal(output_vol, expected_std)

DATA = Path("data/raw_ibkr")

def test_spread_positive():
    bars = pd.read_parquet(DATA / "AAPL_1min.parquet")
    snaps = pd.read_parquet(DATA / "snapshots.parquet")
    out = calc_spread_slippage(bars, "AAPL")
    assert (out['bid_ask_spread'] >= 0).all()
