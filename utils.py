# utils.py  (inside MFS/)
import numpy as np
import pandas as pd
from typing import Union


TRADING_DAYS = 252        # constant

def annualised_volatility(ret_series: pd.Series) -> float:
    """Annualised stdev of daily (log) returns."""
    return ret_series.std() * np.sqrt(TRADING_DAYS)

def sharpe_ratio(ret_series: pd.Series, rf: float = 0.0) -> float:
    """
    Annualised Sharpe ratio.
    rf = daily risk-free rate (use 0 if negligible).
    """
    excess = ret_series - rf
    ann_ret = excess.mean() * TRADING_DAYS
    ann_vol = annualised_volatility(excess)
    return np.nan if ann_vol == 0 else ann_ret / ann_vol

def rolling_vol(
        prices: Union[pd.Series, pd.DataFrame],
        window: int = TRADING_DAYS
) -> Union[pd.Series, pd.DataFrame]:
    """
    Compute the rolling annualized volatility of a price series (or DataFrame).

    Parameters
    ----------
    prices : pd.Series or pd.DataFrame
        Daily price(s). Index should be datetime-like or integer-like.
    window : int
        Number of days to include in each rolling window (default = TRADING_DAYS).

    Returns
    -------
    pd.Series or pd.DataFrame
        Same shape as input minus (window-1) NaN values at the start. 
        Volatility = rolling std of daily returns * sqrt(TRADING_DAYS).
        """
    # 1. Compute simply daily returns: (P_t / P_{t-1} - 1)
    rets = prices.pct_change()

    # 2. Compute rolling std of daily returns
    rolling_std = rets.rolling(window=window).std()

    # 3. Annualize: multiply by sqrt(252)
    ann_vol = rolling_std * np.sqrt(TRADING_DAYS)

    return ann_vol

def rolling_sharpe(
        prices: Union[pd.Series, pd.DataFrame],
        rf: float = 0.0,
        window: int = TRADING_DAYS
) -> Union[pd.Series, pd.DataFrame]:
    """
    Compute the rolling annualized Sharpe ratio of a price series (or DataFrame), assuming a constant annual risk-free rate 'rf'.

    Parameters
    ----------
    prices : pd.Series or pd.DataFrame
        Daily price(s).
    rf : float
        Annual risk-free rate (default = 0.0).
    window : int
        Number of days to include in each rolling window (default = TRADING_DAYS).

    Returns
    -------
    pd.Series or pd.DataFrame
        Same shape as input minus (window-1) NaN values at the start.
    """
    # 1. Compute daily returns
    rets = prices.pct_change()

    # 2. Convert annual risk-free rate to daily
    daily_rf = rf / TRADING_DAYS
    excess_rets = rets - daily_rf

    # 3. Compute rolling mean of excess returns
    roll_mean_excess = excess_rets.rolling(window=window).mean()* TRADING_DAYS

    # 4. Compute rolling std of excess returns
    roll_std_excess = excess_rets.rolling(window=window).std() * np.sqrt(TRADING_DAYS)

    # 5. Calculate Sharpe ratio (annualized mean_excess / annualized std_excess)
    sharpe_ts = roll_mean_excess / roll_std_excess

    return sharpe_ts

import pandas as pd

def calc_spread_slippage(bar_df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Compute spread & slippage purely from high/low/close of 1-min bars.
    """
    bars = bar_df.copy()

    # Use high - low as a proxy for bid-ask spread
    bars['bid_ask_spread']     = bars['high'] - bars['low']
    bars['relative_spread_bps'] = 1e4 * bars['bid_ask_spread'] / bars['close']

    # We don’t have a real mid-quote, so slippage is zero or could be close-mid if you choose
    bars['slippage'] = 0.0

    return bars[['close','bid_ask_spread','relative_spread_bps','slippage']]

