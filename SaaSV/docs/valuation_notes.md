# Week 2
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

# Week 3

#### 2025-07-25  -  Workbook v3
- Added NOL-aware tax block in FCF-Sched tab (rows 25-30)
- Added WACC_inputs tab: live beta picker, Argentina CRP (Damodaran Jul-25), dynamic Ke & WACC outputs
- Added DCF tab: pulls FCF, WACC; PV schedule & TV; outputs EV, equity value, implied share price. 

# Week 4

## 1) Cloud Comps Snapshot (CRM · DDOG · SNOW · NET · MDB)
- **EV/Sales (LTM)** distribution: **P25 = 7.66×**, **Median = 16.32×**, **P75 = 17.10×**.
- **EV/EBITDA (LTM)** is **highly skewed** (several negative EBITDA names): **Median ≈ 20.72×**, tails unreliable (P75 ≈ 184×).
- Conclusion: **Anchor on EV/Sales** for early/scale SaaS; treat EV/EBITDA as secondary due to sample quality.

## 2) Target Positioning (current)
- Inputs: Sales **$4m**, EBITDA **$1m**, Net Debt **$0m**, Shares **10m**, Price **$2.00**.
- Current **EV ≈ $20m** → **EV/Sales ≈ 4.98×** (well **below** peer median 16.32×).
- **Percentile vs peers:** EV/EBITDA rank ≈ **48%** (mid-pack); EV/Sales rank is **well below median**.

## 3) Implied Valuation (peer medians)
- **Sales anchor:** 16.32× × $4m = **$65m EV** → **$6.54 / share** (no net debt).
- **EBITDA anchor:** 20.72× × $1m = **$27m EV** → **$2.66 / share**.
- Takeaway: Fair value range **$2.66–$6.54 / share**; we’ll **cite $6.54** as the primary anchor given comps quality.

## 4) Monte-Carlo DCF (SaaSV_model_v4)
- Drivers: customer **Growth** (40–60–80%), **Decay** (70–75–80%), **Margin** (22–27–32%), **WACC** ~ N(26.97%, 1.5pp).
- **1,000 sims** → Equity value / share: **P10 $1.87 | P50 $2.14 | P90 $2.45**.  
- **Pr(Value > $2.00)** ≈ **74%**. Distribution is tight; upside skew limited by conservative WACC and margins.

## 7) Next Actions
1. Explore **growth–margin correlation** in Monte-Carlo to better capture scaling effects.