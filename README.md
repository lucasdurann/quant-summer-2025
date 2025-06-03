# ────────────────────────────────────────────────────────────────
# Project Road-map & Directory Reference (Week 1 – end of Wed)
# ────────────────────────────────────────────────────────────────

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

