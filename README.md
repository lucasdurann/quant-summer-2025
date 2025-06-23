Project Road-map & Directory Reference 

# Week 1

## 1 Current Tree

quant-summer-2025/
├── courses/
│ └── dc_intro_py_finance/
│ ├── 01_intro_python.ipynb
│ ├── 02_lists.ipynb
│ ├── 03_arrays.ipynb
│ ├── 04_visual_python.ipynb
│ └── … (§ 5 to-do)
│
├── notebooks/ # one-off analysis & mini-projects
│ ├── 01_prices_vs_returns.ipynb # Mini-Proj A (AAPL MSFT SPY)
│ └── 02_sectors_cumrets.ipynb # Mini-Proj B (11 sector ETFs)
│
├── MFS/ # Multi-Factor Strategy research
│ ├── docs/
│ │ └── factor_charter.md
│ ├── data/
│ │ └── ff_factors_5_FF.csv # Fama–French 5-factor table
│ └── fetch_ff_factors.py # script that builds ↑
│
├── data/
│ └── raw_yfinance/
│ ├── prices_10y.parquet # AAPL MSFT SPY (10 y daily)
│ └── sector/
│ └── sector_prices.parquet # 11 SPDR ETF closes
│
├── SaaSV/ # Valuation dataset prep
│ ├── data/filings/ # 10-K PDFs
│ ├── docs/damodaran_links.md
│ └── comp_table.xlsx # comps sheet (starter)
│
├── utils.py # helper functions
│
└── README.md (this file)

## 2 Conventions

| Type of artifact | Folder & rule | Notes |
| ---------------- | ------------- | ----- |
| **Course notebooks** | `courses/dc_intro_py_finance/` | Numbered by chapter |
| **Mini-projects** | `notebooks/0N_*.ipynb` | N = running index |
| **Cached market data** | `data/raw_yfinance/` | Parquet; naming free-form |
| **Research data** | `MFS/data/` | Anything consumed by factor models |
| **Docs / specs** | `*/docs/` | Markdown only |
| **Python helpers** | `utils.py` (top level) | Import with `import utils as ut` |
| **Standalone scripts** | in the folder they update | Paths relative to `__file__` |

## 3 Key helper API (`utils.py`)

```python
import numpy as np

def ann_vol(returns, periods_per_year=252):
    """Annualised volatility of daily/weekly/etc returns."""
    return returns.std(ddof=0) * np.sqrt(periods_per_year)

def sharpe(returns, rf=0.0, periods_per_year=252):
    """Annualised Sharpe ratio (ex-ante RF)."""
    excess = returns - rf/periods_per_year
    return excess.mean() / excess.std(ddof=0) * np.sqrt(periods_per_year)
```
## 4 Completed Deliverables (Week 1)
Deliverable	                                     File	                     Highlight
Mini-Proj A: AAPL/MSFT/SPY returns + scatter	01_prices_vs_returns.ipynb	log-returns, Sharpe & ann vol
Mini-Proj B: 11 sector ETFs cumulative $1	    02_sectors_cumrets.ipynb	plots + ranking table
Fama–French fetcher	                            MFS/fetch_ff_factors.py  	CLI: python MFS/fetch_ff_factors.py
Factor Charter (draft)	                        MFS/docs/factor_charter.md	universe + factors + rules

## 5 Git Cheatsheet
git init                                # already done
git remote add origin <YOUR_GH_URL>     # one-time
git add <paths>                         # stage
git commit -m "msg"                     # commit
git push -u origin main                 # first push

# Week 2

## 1 Quick API smoke-test
python ibkr_connect.py                   # prints TWS server time

## 2 Fetched 1-min bars for AAPL, SPY via IBKR API; stored to Parquet.

## 3 📊 Seed Factor Pipeline — Week 2  

A lightweight **3-factor snapshot** to kick-start the MFS (Multi-Factor Strategy) workstream.  

| Detail | Implementation |
|--------|----------------|
| **Universe** | 30 large-cap U.S. tickers (see `TICKERS` list in `factor_pipeline.py`). |
| **Data sources** | *Prices* & *fundamentals* via **yfinance** (auto-adjusted daily closes, .info key stats). |
| **Factors** | *Value* = inverse Price-to-Sales (TTM)  <br>*Momentum* = 12-month total return  <br>*Quality* = Return-on-Equity (proxy, 1-yr). |
| **Scoring** | In-sample **z-scores** for each factor → simple average to get **`composite`** rank. |
| **Output** | CSV written to `data/mfs/factors_snapshot_YYYYMMDD.csv` (dated each run). |

#### How to reproduce

```bash
# from repo root
python MFS/factor_pipeline.py
```

## 4 Demo limit order (AAPL, 10 sh) submitted & cancelled

## 5 Added bid-ask spread & slippage helper in utils.py; unit test passing

## 6 Multi Factor Strategy code in quantconnect

### Algorithm in Finance Terms

Universe filter --> stay in liquid, trade-able names. Keep only U.S. equities trading above $10 and rank them by dollar-volume; keep only top 200

Momentum ranking --> Chase price momentum. Look at the total return over the last 252 trading days for the stocks we had left. Measure "winners keep winning" effect; the higher the return the last 12 months, the higher the score

Value ranking --> Chase stock value. Look at the price to sales ratio; the lower the ratio the better (that is why we invert it in next steps)

Quality ranking --> Chase quality stocks. Take the ROE on each of the stocks; the higher the better

Z-Score --> We z-score each of the factors to get a standardized value so that we can compare each of the variables with each other. Since in the case of value, the lower the better, we invert the method to take the z-score, so that this corresponds.

Composite --> We add up the factors giving the same weight to each of them, we sort them out and we stay with the 10 highest stocks in this composite. 

Investing --> Finally we invest in the 10 stocks giving the same weight to each of them. 

##