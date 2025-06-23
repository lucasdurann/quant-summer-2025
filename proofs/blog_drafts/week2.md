### From CSVs to Live Orders – Week 2 Recap 

**Data plumbing → signals**  
I kicked off the week by wiring IBKR’s API into a local data lake. One 10-line script now pulls 1-minute bars for AAPL & SPY and snapshots the quotes to Parquet. With clean price history in hand, I spun up a minimal three-factor pipeline (Value, Momentum, Quality) and saved the first composite-rank CSV. The numbers finally looked “investable.”

**Signals → action**  
Tuesday’s victory lap was an API smoke-test: submit a 10-share AAPL limit order, watch it hit *Submitted*, then cancel. Nothing filled—and that was the point. Seeing the order bounce through IBKR’s status callbacks proved I can move from read-only analytics to write-enabled execution whenever the strategy is ready.

**Action → strategy scaffold**  
Mid-week I hardened the SaaS valuation model: OpEx is now %-of-revenue, DSO/DPO feed Δ Working Capital, and unlevered FCF finally emerges. Parallel to that, I bootstrapped a QuantConnect environment. The first cloud back-test replicates my factor logic natively inside QC, rebalancing the top-10 composite scorers each month from 2019-24.

**Algorithm Code in quantconnect**
Last part of the week (and more time than expeceted) I spend it on wiring an algorihtm via coding to use the three-factor previously spoken (although I had to refetched them and reorder them in quantconnect due to pracitcality) and invest in the 10 stocks more valuable given the composite of this factors, rebalancing each month

**Why it matters**  
Week 1 produced static notebooks; Week 2 stitched them into a living pipeline—from raw ticks to factor ranks, to trial orders, to a cloud strategy—all under version control. Next up: scale the universe, add risk filters, and test live brokerage routing.
