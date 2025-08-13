# Bridging Quant & Valuation – Week 4

This week I tightened the trading model and added uncertainty to the valuation stack.

**On the trading side**, I kept the simple composite factor (momentum + value + quality) and moved from long-only to a clean long–short: top-10 names long, bottom-5 short. Sizing stays volatility-scaled with a 13% per-name cap and a 15% trailing stop. The result (v05) materially improves total return vs the earlier long-only baseline while keeping the code compact and readable. *Return ~260% over 2019–24*.

**On the valuation side**, I added a Monte-Carlo tab to the SaaS model. Instead of a single fair value, the model now draws Growth, Decay and Margin, and samples WACC to produce a distribution of **Equity Value per share**. From 1,000 sims: **P10 \$1.87 • Median \$2.14 • P90 \$2.45**, with ~74% of outcomes above today’s price.

Why this matters: the trading system now expresses relative views (long–short), and the DCF outputs a probability, not a point guess—so position sizing and exits can reference both risk and valuation.

**Next up**: walk-forward validation and an explicit commission/slippage model; then decide whether to stand up Lean CLI for live paper.
