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

# Week 3 - 

## Day 2 - GARCH Vol-Forecast & **`vol_cap`** Risk-Parity Hook
| Deliverable | Path | Purpose |
|--------------|------|---------|
| **Notebook** | `notebooks/06_garch_irs.ipynb` | Fits a Student-t **GARCH(1, 1)** to daily log-returns of *IRS* ADR (2015-2025). Generates next-day σ̂ series and saves comparison plot vs. realised 22-day σ. |
| **Chart** | `proofs/img/garch_irs_sigma.png` | Visual proof of volatility clustering & model fit — used in Week-3 Dev-Log + LinkedIn snippet. |
| **Helper** | `utils.py` → `forecast_vol()` | Caches GARCH fits & returns σ̂ series for any ticker. Signature:<br>`forecast_vol(series_or_path, p=1, q=1, horizon=1, scale_pct=True)` |
| **Unit test** | `tests/test_stats.py` | Basic shape & non-null assertions for `forecast_vol()`. |
| **Factor snapshot** | `MFS/data/factors_snapshot_YYYYMMDD.csv` | Pipeline now appends a **`vol_cap`** column where `vol_cap = 1 / σ̂`. Caps position size inversely to forecast volatility (simple risk-parity). |
| **Pipeline update** | `MFS/factor_pipeline.py` | Loops through tickers → calls `forecast_vol()` → injects `vol_cap` → exports new snapshot. |

#### Quick Usage
```python
from utils import forecast_vol
import pandas as pd

price_series = pd.read_parquet("data/raw_yfinance/prices_arg.parquet")["IRS"]
sigma_hat    = forecast_vol(price_series, horizon=1)      # σ̂ 1-day ahead
vol_cap      = 1 / sigma_hat 
```

#### Key Takeaways
- Adaptive risk sizing — positions will now down-weight during high-vol windows and scale up when volatility subsides.
- Reusable tooling — forecast_vol() is ticker-agnostic; the back-tester and future factor pipelines can call it directly.
- Performance ready — GARCH fit cached with @lru_cache; unit test green; CI passes.

## Day 7 - QuantConnect code updated with vol_cap
| v0.2 | 2019‑24 | vol_cap weights | [JSON](/quantconnect/backtests/v0.2.json) |

# Week 4 - From Back-test to Live Paper & Valuation Monte-Carlo
## Day 1 Wednesday - vol_cap QC code update
- Updated QuantConnect code with vol_cap for volatility consideration and volatility weight using the same metrics as before.
- Also coded the notifications system and debug for live trade, though for the moment not working since it is a paid function in QC, not paying for now. Tried one time the live option, since the first one is free. We will continue to prepare the code for the eventual live option, but for now not live trading.

## Day 2 Thursday - Guardrails QC code update
**Current config**
- Dates: 2019-01-01 → 2024-12-31
- Cap: **13 % of NAV per symbol**
- Stop: **Trailing**, **15 %**
- Backtest JSON: `quantconnect/backtests/backtest_v03.json`

### Core Results — Before vs After
| Run | CAGR | Sharpe | Max-DD | Orders |
|---|---:|---:|---:|---:|
| v02 (pre-guardrail) | 12.06% | 0.367 | 62.3% | 979 |
| **v03 (guardrails)** | **16.04%** | **0.493** | **54.3%** | **607** |

Cap and Stop actual settings are the best from the ones tried (Caps tried: 8%/10%/13% | Stops tried 10%/12%/15% all trailing)

## Day 3 Friday - v04 SaaSV model
### Monte-Carlo Valuation (added in **SaaSV_model_v4.xlsx**)

| Item | Details |
|------|---------|
| **Sheet** | `Monte-Carlo`  (duplicated v3 → **v4**) |
| **Stochastic drivers** | • **Customer Growth Rate**: triangular 40 – 60 – 80 %  <br>• **Growth-Decay Factor**: triangular 70 – 75 – 80 %  <br>• **EBIT Margin**: triangular 22 – 27 – 32 %  <br>• **WACC**: 𝑁(26.97 %, 1.5 pp) |
| **Simulation engine** | Excel **Data ▶ What-If ▶ Data Table**, 1 000 rows (SimID 1-1000) |
| **Output captured** | Equity Value / share → column `EV_per_share` |
| **Summary statistics** | P10 **$1.87**  ·  Median **$2.14**  ·  P90 **$2.45**  ·  **74 %** of sims exceed current market price |
| **Visual** | Histogram saved: `proofs/img/saasv_mc_hist_v1.png` |
| **Toggle** | Cell `Monte-Carlo!J1` = **ON/OFF** to switch between base and stochastic inputs |

> *Purpose:* replaces deterministic DCF with probability distribution, enabling risk-aware sizing and exit rules.

### Comp_table_v2 - Added Snapshot of Companies, Target Positioning and Implied Valuation using peer medians
**Cloud Comps Snapshot (CRM · DDOG · SNOW · NET · MDB)**
- **EV/Sales (LTM)** distribution: **P25 = 7.66×**, **Median = 16.32×**, **P75 = 17.10×**.
- **EV/EBITDA (LTM)** is **highly skewed** (several negative EBITDA names): **Median ≈ 20.72×**, tails unreliable (P75 ≈ 184×).
- Conclusion: **Anchor on EV/Sales** for early/scale SaaS; treat EV/EBITDA as secondary due to sample quality.

**Target Positioning (current)**
- Inputs: Sales **$4m**, EBITDA **$1m**, Net Debt **$0m**, Shares **10m**, Price **$2.00**.
- Current **EV ≈ $20m** → **EV/Sales ≈ 4.98×** (well **below** peer median 16.32×).
- **Percentile vs peers:** EV/EBITDA rank ≈ **48%** (mid-pack); EV/Sales rank is **well below median**.

**Implied Valuation (peer medians)**
- **Sales anchor:** 16.32× × $4m = **$65m EV** → **$6.54 / share** (no net debt).
- **EBITDA anchor:** 20.72× × $1m = **$27m EV** → **$2.66 / share**.
- Takeaway: Fair value range **$2.66–$6.54 / share**; we’ll **cite $6.54** as the primary anchor given comps quality.

