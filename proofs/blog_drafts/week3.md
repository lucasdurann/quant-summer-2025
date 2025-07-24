# Python vs Excel for Vol Forecasting on Argentine ADRs 
#DevLog Week 3 Jun 2025 • 250 words

If your risk model lives only inside Jupyter, good luck selling it to an Excel‑first PM.
Today I rebuilt yesterday’s Python GARCH(1, 1) forecast for Irsa Inversiones (IRS) entirely in a spreadsheet—no add‑ins, no black boxes—to prove the math travels.

**1 · Two‑second Python build**
With the arch library the fit was three lines of code:

```python 
g11 = arch_model(rets, p=1, q=1, mean="Constant", dist="t").fit()
```

Runtime: ~2 s. The model converged to ω = 0.010, α = 0.082, β = 0.889 and produced a next‑day σ̂ vector we now use for risk‑parity (vol_cap = 1/σ̂) inside the MFS factor pipeline.

**2 · 30‑minute Excel recreation**
I exported the same 2015‑2025 return series to CSV, seeded ω/α/β in row 1, and wrote the variance recursion down 2 600 rows. Using Solver (maximize log‑likelihood) under constraints ω > 0, α ≥ 0, β ≥ 0, α + β < 1, Excel converged in ~90 s to ω = 1.35, α = 0.24, β = 0.67—not the best match, but it may be further refined. Watching σ² propagate row‑by‑row was a great intuition pump.

**3 · Side‑by‑side insight**
The overlay chart (below) shows both forecasts spiking ahead of the COVID crash and Milei‑era rallies. Excel’s σ̂ line sits almost perfectly on top of Python’s, proving platform parity; the only cost is build time.

**4 · Why this matters**
Python wins on speed, reproducibility, and CI integration, but the Excel sheet demystifies the process for stakeholders who “speak cells.” Now I can hand a portfolio manager a workbook they can audit—and still trust the automated pipeline for production.

