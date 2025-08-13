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
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100_000)
        self.num_stocks = 10
        self.selected = []
        self.vol_window = 260                                           # ~1y of daily bars
        self.sigma_cache = {}                                           # {symbol: (last_bar_time, sigma)}
        self.SetRiskManagement(MaximumDrawdownPercentPerSecurity(0.15)) # 15% max drawdown
        self.min_sector_names = 8                                       # fallback to cross-section z if sector is tiny
        self.clip_q = 0.02                                              # winsorize at 2%/98% inside sector
        self.rebalance_count = 0

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

    def _sector_code(self, f):
        """Return an int sector code; fallback -1 if missing."""
        try:
            ac = f.AssetClassification
            code = ac.MorningstarSectorCode
            if code is not None:
                return int(code)
        except Exception:
            pass
        # older field fallback (rare)
        try:
            return int(f.CompanyReference.IndustryTemplateCode)
        except Exception:
            return -1

    def _sector_neutral_z(self, df, col, invert=False):
        """
        Sector-neutral z for column `col` with within-sector winsorization.
        Fallback to global z for small sectors or zero stdev.
        """
        x = df[col].astype(float)
        # precompute global stats for fallback
        gx = x.clip(x.quantile(self.clip_q), x.quantile(1 - self.clip_q))
        gmu, gsig = float(gx.mean()), float(gx.std(ddof=0) or 1e-9)

        def per_sector(g):
            if len(g) < self.min_sector_names:
                # fallback: global z for this group
                return (g[col].clip(gx.quantile(self.clip_q), gx.quantile(1 - self.clip_q)) - gmu) / gsig
            # winsorize within sector
            lo, hi = g[col].quantile(self.clip_q), g[col].quantile(1 - self.clip_q)
            xc = g[col].clip(lo, hi)
            mu = float(xc.mean())
            sig = float(xc.std(ddof=0) or 1e-9)
            return (xc - mu) / sig

        z = df.groupby("sector", group_keys=False).apply(per_sector).astype(float)
        if invert:   # value low = good
            z = -z
        return z

    # ---------- step 2: compute 12-mo momentum ----------
    def FineSelection(self, fine):
        records = []
        for f in fine:
            # --- Momentum (12-mo total return) ---
            hist = self.History(f.Symbol, 252, Resolution.Daily)
            if hist.empty or len(hist.close) < 2:
                continue
            mom = float(hist["close"][-1] / hist["close"][0] - 1)

            # --- Value (P/S) ---
            ps_raw = f.ValuationRatios.sales_yield   # already 1/(P/S) in QC
            if ps_raw is None or ps_raw <= 0:
                continue
            ps = float(ps_raw)

            # --- Quality (ROE) ---
            roe_raw = f.OperationRatios.ROE.Value
            if roe_raw is None:
                continue
            roe = float(roe_raw)

            records.append({
                "symbol": f.Symbol,
                "sector": self._sector_code(f),
                "momentum": mom,
                "value": ps,
                "quality": roe
            })

        if not records:
            return self.selected  # keep last universe if nothing valid

        df = pd.DataFrame(records)

        # === sector-neutral z-scores ===
        df["z_mom"]  = self._sector_neutral_z(df, "momentum", invert=False)
        df["z_val"]  = self._sector_neutral_z(df, "value",    invert=True)   # value: low price = good
        df["z_qual"] = self._sector_neutral_z(df, "quality",  invert=False)

        # composite: equally-weighted
        df["composite"] = (df["z_mom"] + df["z_val"] + df["z_qual"]) / 3.0

        # pick top N
        self.selected = df.sort_values("composite", ascending=False).head(self.num_stocks)["symbol"].tolist()
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
        CAP = 0.13  # cap at 13% per stock
        for s in list(self.Portfolio.Keys):
            if self.Portfolio[s].Invested and s not in self.selected:
                    self.Liquidate(s)         
        for s, w in weights.items():
            w_capped = min(w, CAP)  # cap at 13%
            self.SetHoldings(s, float(round(w_capped, 4)))