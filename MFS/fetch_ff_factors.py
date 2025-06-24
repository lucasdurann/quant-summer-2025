# fetch_ff_factors.py

"""
A small script to fetch the Fama–French 5‐Factor data table
from Kenneth French’s website and save it to a local CSV.

Usage:
    python fetch_ff_factors.py

This script will:
  1. Check that MFS/data/ exists (and create it if not).
  2. Use pandas_datareader to pull down the “F-F_Research_Data_5_Factors_2x3” dataset.
  3. Write the factors (monthly) to MFS/data/ff_factors_5_FF.csv.
"""

import os
from pathlib import Path

import pandas as pd
import pandas_datareader.data as web
from datetime import datetime


def fetch_and_save_ff5(csv_path: Path, start_date: str = "1963-07-01"):
    """
    Fetch the Fama–French 5 factors from Ken French's library and write to CSV.

    By default, start from July 1963 (the inception of the 5‐factor series).
    """

    # 1) Use DataReader to get the “F-F_Research_Data_5_Factors_2x3” table (monthly data)
    #    (The returned object is a dict of DataFrames; the first entry [0] is the raw factors table.)
    print(f"Fetching Fama–French 5 factors (monthly) since {start_date} ...")
    ff_raw = web.DataReader('F-F_Research_Data_5_Factors_2x3', 'famafrench', start=start_date)

    # The dictionary keys are like {0: DataFrame_of_factors, 1: some extra metadata, ...}
    # We only need the first DataFrame (index 0).
    if 0 not in ff_raw:
        raise KeyError("Unexpected structure: DataReader did not return ff_raw[0].")
    ff5_df = ff_raw[0]

    # 2) The index (YEAR‐MONTH) is currently an integer like 196301 for January 1963.
    #    Let’s convert that index into a pandas PeriodIndex or Timestamp.
    #    The “Period” approach helps us write YYYY-MM to CSV, but we can also do Timestamp.
    #    Below, we will convert to strings of form 'YYYY-MM-01' for clarity.

    # Convert the integer index (e.g. 196301 → datetime(1963,1,1))
    def int_to_timestamp(imonth):
        if isinstance(imonth, pd, Period):
            return imonth.to_timestamp()
        s = str(int(imonth))
        year = int(s[:4])
        month = int(s[4:])
        return datetime(year, month, 1)

    # If the index is already a PeriodIndex, convert it to Timestamp directly:
    if isinstance(ff5_df.index, pd.PeriodIndex):
      ff5_df.index = ff5_df.index.to_timestamp()

# Otherwise (older pandas_datareader), assume the index is integer‐like and do int_to_timestamp:
    else:
      ff5_df.index = ff5_df.index.map(int_to_timestamp)

    # 3) Now write out the DataFrame to CSV
    print(f"Writing to CSV: {csv_path}")
    ff5_df.to_csv(csv_path)
    print("Done.")


if __name__ == "__main__":
    # Determine project‐root relative path
    # (If you run this script from anywhere, it will always save to MFS/data.)
    project_root = Path(__file__).resolve().parent  # this is “.../quant-summer-2025/MFS”
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    # Path to the CSV we want to create
    out_file = data_dir / "ff_factors_5_FF.csv"

        # **ACTUAL CALL**: fetch the 5‐factor data and write it out
    fetch_and_save_ff5(out_file, start_date="1963-07-01")