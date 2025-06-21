from AlgorithmImports import *
import pandas as pd 
import numpy as np 

class TopCompositeFactor(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100_000)
        self.num_stocks = 10
        self.selected = []

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

    # ---------- monthly rebalance ----------
    def Rebalance(self):
        weight = 1 / self.num_stocks
        for kvp in self.Portfolio:
            if kvp.Value.Invested and kvp.Key not in self.selected:
                self.Liquidate(kvp.Key)
        for s in self.selected:
            self.SetHoldings(s, weight)
