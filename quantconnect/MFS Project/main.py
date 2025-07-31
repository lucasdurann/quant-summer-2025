from AlgorithmImports import *
import pandas as pd 
import numpy as np 
from collections import defaultdict
import math
try:
    from arch import arch_model        # for GARCH volatility estimation    
    GARCH_OK = True
except ImportError:
    GARCH_OK = False

class TopCompositeFactor(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100_000)
        self.num_stocks = 10
        self.selected = []
        self.vol_window = 260              # ~1y of daily bars
        self.sigma_cache = {}              # {symbol: (last_bar_time, sigma)}

        self.spy = self.AddEquity("SPY").Symbol

        # === Universe selection hooks ===
        self.AddUniverse(self.CoarseSelection, self.FineSelection)

        # Schedule a monthly rebalance 10 min after market open
        self.Schedule.On(self.DateRules.MonthStart(),
                         self.TimeRules.AfterMarketOpen(self.spy, 10),
                         self.Rebalance)

        self.selected = []     # store current portfolio symbols

    # ---------- step 1: narrow to liquid stocks ----------
    def CoarseSelection(self, coarse):
        # filter for price > $10, keep top 200 by dollar volume
        liquid = [x for x in coarse if x.Price > 10]
        top_liquid = sorted(liquid, key=lambda x: x.DollarVolume, reverse=True)[:200]
        return [x.Symbol for x in top_liquid]

    # ---------- step 2: compute 12-mo momentum ----------
    def FineSelection(self, fine):
        records = []
        for f in fine:
            # --- Momentum (12-mo total return) ---
            hist = self.History(f.Symbol, 252, Resolution.Daily)
            if hist.empty: continue
            mom = float((hist["close"][-1] / hist["close"][0]) - 1)
        
            # --- Value (P/S) ---
            ps_raw = f.ValuationRatios.sales_yield
            if ps_raw <= 0 or ps_raw is None: continue     #skip invalid
            ps = float (ps_raw)

            # --- Quality (ROE) ---
            roe_raw = f.OperationRatios.ROE.Value
            if roe_raw is None: continue
            roe = float (roe_raw)

            records.append({
                "symbol": f.Symbol,
                "momentum": mom,
                "value": ps,
                "quality": roe
            })
        if len(records) == 0:
            return self.selected     # fallback to previous set

        # EARLY EXIT if we have no valid records
        if not records:
            return self.selected  # keep last month’s universe

        df = pd.DataFrame(records)

        # z-scores: momentum / quality high is good, value low is good
        df["z_mom"] = (df["momentum"] - df["momentum"].mean()) / df["momentum"].std(ddof=0)
        df["z_val"] = (df["value"].mean() - df["value"]) / df["value"].std(ddof=0)   # inverted
        df["z_qual"] = (df["quality"] - df["quality"].mean()) / df["quality"].std(ddof=0)

        df["composite"] = (df["z_mom"] + df["z_val"] + df["z_qual"]) / 3
        df = df.sort_values("composite", ascending=False)

        self.selected = df.head(self.num_stocks)["symbol"].tolist()
        return self.selected

    # ---------- step 3: compute volatility ----------
    def ForecastSigma(self, symbol):
         """Return next‑day σ forecast in %."""
         last_time, sig = self.sigma_cache.get(symbol, (None, None))
       # update only once per month (after rebalance)
         if last_time is not None and last_time.month == self.Time.month:
            return sig

         hist = self.History(symbol, self.vol_window, Resolution.Daily)
         if hist.empty or len(hist.close) < 30:
           sig = 30       # fallback 30 % if we lack data
         else:
           rets = (np.log(hist.close).diff().dropna() * 100)  # % log‑ret
           if GARCH_OK:
               am  = arch_model(rets, p=1, q=1, mean='Zero',
                                vol='GARCH', dist='t')
               res = am.fit(disp="off")
               var = res.forecast(horizon=1).variance.iloc[-1, 0]
               sig = math.sqrt(var)
           else:
               sig = rets.rolling(22).std().iloc[-1]           # realised σ

         self.sigma_cache[symbol] = (self.Time, sig)
         return sig

    # ---------- monthly rebalance ----------
    def Rebalance(self):
        weight = 1 / self.num_stocks
        sigmas = {s: self.ForecastSigma(s) for s in self.selected}
        avg_sigma = np.mean(list(sigmas.values()))

        raw_w = {s:1 / self.num_stocks * min (avg_sigma / sig, 1)
                 for s, sig in sigmas.items()}    # vol_cap = avgσ/σ̂
        # normalise so weights sum ≈ 1 (optional but nice for comparability)
        total = sum(raw_w.values())
        weights = {s: w / total for s, w in raw_w.items()}
        for kvp in self.Portfolio:
            if kvp.Value.Invested and kvp.Key not in self.selected:
                self.Liquidate(kvp.Key)
        for s in self.selected:
            self.SetHoldings(s, weight)
        for s, w in weights.items():
            self.SetHoldings(s, float(w))

    def OnOrderEvent(self, order_event: OrderEvent):
        if order_event.Status != OrderStatus.Filled:
            return

        ticket   = self.Transactions.GetOrderById(order_event.OrderId)
        fill_val = abs(order_event.FillPrice * order_event.FillQuantity)

        # --- DEBUG LINE (always) ---
        self.Debug(f"Order {ticket.Id} | {ticket.Symbol} "
                   f"{ticket.Direction.name} {ticket.Quantity} @ {order_event.FillPrice:.2f} "
                   f"| ${fill_val:,.0f}")

        # --- EMAIL ALERT (> $1 000) ---
        if fill_val > 1_000:
            subject = f"Big Fill ${fill_val:,.0f} – {ticket.Symbol}"
            body    = f"{self.Time:%Y-%m-%d %H:%M}  {ticket.Direction.name} " \
                      f"{ticket.Quantity} {ticket.Symbol} @ {order_event.FillPrice:.2f}"
            self.Notify.Email(subject, body)
