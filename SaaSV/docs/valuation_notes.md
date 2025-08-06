#### 2025-06-23  •  FCF schedule (v2)

* Cash tax rate: **25 %** hard-coded (placeholder until we layer NOLs).
* D&A and CapEx each **2 % of revenue** to model maintenance spend.
* Δ Net Working Capital links to Drivers-based DSO/DPO outputs.
* Sensitivity grid shows FCF hit/boost of ±5 % rev growth:
  | Year | Bear (-5 %) | Base | Bull (+5 %) |
  |------|-------------|------|-------------|
  | 2024 | $1780 th | $1874 th | $1967 th |
  | 2025 | $2668 th | $2809 th | $2949 th |
  | 2026 | $3728 th | $3924 th | $4120 th |
  | 2027 | $4886 th | $5143 th | $5400 th |
  | 2028 | $4544 th | $4783 th | $5022 th |

* Observation: Model is more sensitive to top-line than margin tweaks; next step is WACC/DCF in Week 5.

#### 2025-07-25  -  Workbook v3
- Added NOL-aware tax block in FCF-Sched tab (rows 25-30)
- Added WACC_inputs tab: live beta picker, Argentina CRP (Damodaran Jul-25), dynamic Ke & WACC outputs
- Added DCF tab: pulls FCF, WACC; PV schedule & TV; outputs EV, equity value, implied share price. 

#### 2025-07-25 - Workbook v4
Monte-Carlo Valuation (added in **SaaSV_model_v4.xlsx**)

| Item | Details |
|------|---------|
| **Sheet** | `Monte-Carlo`  (duplicated v3 → **v4**) |
| **Stochastic drivers** | • **Customer Growth Rate**: triangular 40 – 60 – 80 %  <br>• **Growth-Decay Factor**: triangular 70 – 75 – 80 %  <br>• **EBIT Margin**: triangular 22 – 27 – 32 %  <br>• **WACC**: 𝑁(26.97 %, 1.5 pp) |
| **Simulation engine** | Excel **Data ▶ What-If ▶ Data Table**, 1 000 rows (SimID 1-1000) |
| **Output captured** | Equity Value / share → column `EV_per_share` |
| **Summary statistics** | P10 **$1.87**  ·  Median **$2.14**  ·  P90 **$2.45**  ·  **74 %** of sims exceed current market price |
| **Visual** | Histogram saved: `proofs/img/saasv_mc_hist_v1.png` |
| **Toggle** | Cell `Monte-Carlo!J1` = **ON/OFF** to switch between base and stochastic inputs |