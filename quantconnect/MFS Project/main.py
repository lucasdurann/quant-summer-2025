from operator import invert
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
from QuantConnect.Algorithm.Framework.Risk import MaximumDrawdownPercentPerSecurity

class TopCompositeFactor(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100_000)
        self.num_stocks = 15
        self.selected = []
        self.vol_window = 260                                           # ~1y of daily bars
        self.sigma_cache = {}                                           # {symbol: (last_bar_time, sigma)}
        self.SetRiskManagement(MaximumDrawdownPercentPerSecurity(0.15)) # 15% max drawdown      
        self.rebalance_count = 0

         # long-short controls
        self.long_count   = 10     # top N longs
        self.short_count  = 5      # bottom N shorts
        self.gross_target = 1.50   # |long| + |short| as % of NAV (e.g., 150%)
        self.net_target   = 1.00   # long minus short as % of NAV (100% net long)


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
            hist = self.History(f.Symbol, 252, Resolution.Daily)  # 252 days momentum history
            if hist.empty or len(hist.close) < 2: continue
            mom = float(hist["close"][-1] / hist["close"][0] - 1) 
    
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
        
        # long the top N, short the bottom N
        longs  = df.sort_values("composite", ascending=False).head(self.long_count)["symbol"].tolist()
        shorts = df.sort_values("composite", ascending=True ).head(self.short_count)["symbol"].tolist()

        self.longs  = longs
        self.shorts = shorts
        self.selected = longs + shorts        # universe we actually trade
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
        # Liquidate names no longer in selection
        for kvp in list(self.Portfolio.Values):
            if kvp.Invested and kvp.Symbol not in set(self.selected):
                self.Liquidate(kvp.Symbol)

        if not getattr(self, "longs", None) and not getattr(self, "shorts", None):
            return

        # Targets from gross/net
        L_target = (self.gross_target + self.net_target) / 2.0   # long dollars / NAV
        S_target = (self.gross_target - self.net_target) / 2.0   # short dollars / NAV (positive number)

        # --- helper to build vol-scaled weights for a list of symbols ---
        def leg_weights(syms, target_long_fraction):
            if not syms or target_long_fraction <= 0:
                return {}
            sigmas = {s: self.ForecastSigma(s) for s in syms}
            avg_sig = float(np.mean(list(sigmas.values())))
            raw = {s: min(avg_sig / max(sig, 1e-9), 1.0) for s, sig in sigmas.items()}
            total = sum(raw.values())
            if total <= 0:
                return {}
            # scale to target
            w = {s: target_long_fraction * v / total for s, v in raw.items()}
            return w

        w_long  = leg_weights(self.longs,  L_target)
        w_short = leg_weights(self.shorts, S_target)
        # flip sign for shorts
        w_short = {s: -v for s, v in w_short.items()}

        # 13% absolute cap per position
        CAP = 0.13
        for s in list(w_long.keys()):
            w_long[s] = min(w_long[s], CAP)
        for s in list(w_short.keys()):
            w_short[s] = -min(abs(w_short[s]), CAP)

        # Combine and place orders
        weights = {}
        weights.update(w_long)
        weights.update(w_short)

        # Set target holdings (rounded for cleaner logs)
        for s, w in weights.items():
            self.SetHoldings(s, float(round(w, 4)))