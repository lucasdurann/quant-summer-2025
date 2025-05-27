# Factor Charter – Multi-Factor Stock-Selection (Draft v0)

> **Goal**: Outperform the S&P 500 by selecting the top-quintile of stocks
> ranked on Value, Momentum, and Quality signals, rebalanced monthly.

---

## 1 Universe & Data

| Aspect | Choice |
|--------|--------|
| Symbols | **S&P 500 constituents** (live membership) |
| Data sources | **Yahoo Finance** via `yfinance` for prices + fundamentals |
| Date range | **2014-01-01 → 2024-04-30** |
| Currency | USD |
| Corporate actions | Prices adjusted for splits & dividends |

---

## 2 Factor Definitions

| Factor | Formula | Rationale |
|--------|---------|-----------|
| **Value** | `EBIT / Enterprise Value` | Cheaper earnings vs. capital |
| **Momentum** | Total return **t-12 to t-1 m** | Price persistence effect |
| **Quality** | `Return on Equity` (TTM) | Profitable, well-run firms |

*All factors **winsorised (1 % tails)** then **z-scored** to standardise.*

---

## 3 Scoring & Ranking

1. Compute **z-score** for each factor within the universe.  
2. **Composite score** = simple average of the three z-scores.  
3. Rank descending; select **top 20 % (≈100 stocks)** each rebalance.

---

## 4 Portfolio Construction Rules

* Weighting   : **Equal weight** across selected names  
* Rebalance freq.: **Monthly** (first trading day)  
* Turnover cap  : Skip trade if target weight change < 0.25 %  
* Position cap  : max 2 % NAV per security  
* Cash drag    : residual cash left uninvested

---

## 5 Back-test Parameters

| Parameter | Setting |
|-----------|---------|
| Initial capital | \$1 000 000 |
| Commission | \$0.001 per share |
| Slippage | 5 bp per trade |
| Benchmark | **SPY ETF** |
| Reinvestment | Dividends reinvested |

---

## 6 Key Performance Indicators to Collect

* Annualised return & volatility  
* Sharpe ratio  
* Maximum draw-down  
* CAGR vs. SPY  
* Monthly turnover

---

## 7 Next Steps

1. Code factor pipeline (`factor_pipeline.py`) and unit tests.  
2. Run small-scale back-test in **`factor_backtest.ipynb`** with 10 stocks to verify maths.  
3. Expand to full universe and capture KPIs for Charter “Initial Results” section.
