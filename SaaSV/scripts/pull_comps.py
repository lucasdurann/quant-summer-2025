#!/usr/bin/env python
# scripts/pull_comps_csv.py  (v2 robust shares/market cap)
from __future__ import annotations
import argparse, datetime as dt, pathlib, sys
import pandas as pd
import yfinance as yf

DEF_TICKERS = ["CRM", "DDOG", "SNOW", "NET", "MDB"]
OUTDIR = pathlib.Path("SaaSv/data/comps")

def latest_shares(t: yf.Ticker) -> float | None:
    """Best-effort shares outstanding."""
    fi = getattr(t, "fast_info", {}) or {}
    shares = fi.get("shares_outstanding") or fi.get("sharesOutstanding")
    if shares:
        return float(shares)
    # Fallback: time series
    try:
        sh = t.get_shares_full()
        if isinstance(sh, pd.Series) and not sh.dropna().empty:
            return float(sh.dropna().iloc[-1])
    except Exception:
        pass
    # Last resort: info dict (slower / may deprecate)
    try:
        info = t.get_info()
        m = info.get("sharesOutstanding")
        if m:
            return float(m)
    except Exception:
        pass
    return None

def latest_market_cap(t: yf.Ticker) -> float | None:
    fi = getattr(t, "fast_info", {}) or {}
    mc = fi.get("market_cap") or fi.get("marketCap")
    if mc:
        return float(mc)
    try:
        info = t.get_info()
        m = info.get("marketCap")
        return float(m) if m else None
    except Exception:
        return None

def fetch_one(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    fi = getattr(t, "fast_info", {}) or {}

    price  = float(fi.get("last_price") or fi.get("lastPrice") or 0.0) or None
    shares = latest_shares(t)
    # Prefer computed market cap; else fallback to provider value
    market_cap = (price * shares) if (price and shares) else latest_market_cap(t)

    inc_q = t.get_income_stmt(freq="quarterly")
    bs_q  = t.get_balance_sheet(freq="quarterly")

    asof_income  = str(inc_q.columns[0].date()) if inc_q.shape[1] else ""
    asof_balance = str(bs_q.columns[0].date())  if bs_q.shape[1] else ""

    def _first(df: pd.DataFrame, keys):
        for k in keys:
            if k in df.index:
                s = df.loc[k].dropna()
                if not s.empty:
                    return float(s.iloc[0])
        return None

    def _sum_last4(df: pd.DataFrame, keys):
        for k in keys:
            if k in df.index:
                s = df.loc[k].dropna()
                if s.shape[0] >= 4:
                    return float(s.iloc[:4].sum())
                return float(s.sum()) if not s.empty else None
        return None

    revenue_ttm = _sum_last4(inc_q, ["TotalRevenue", "totalRevenue", "Revenue"])
    ebitda_ttm  = _sum_last4(inc_q, ["EBITDA", "ebitda"])

    cash_q = _first(bs_q, ["CashAndCashEquivalents",
                           "CashCashEquivalentsAndShortTermInvestments",
                           "CashAndShortTermInvestments", "Cash"])
    total_debt_q = _first(bs_q, ["TotalDebt", "ShortLongTermDebtTotal",
                                 "LongTermDebtAndCapitalLeaseObligation"])
    if total_debt_q is None:
        short = _first(bs_q, ["ShortTermDebt", "CurrentPortionOfLongTermDebt"])
        long  = _first(bs_q, ["LongTermDebt", "LongTermDebtNoncurrent"])
        if short is not None or long is not None:
            total_debt_q = (short or 0.0) + (long or 0.0)

    currency = str(fi.get("currency") or "")

    return {
        "ticker": ticker,
        "price": price,
        "shares_out": shares,
        "market_cap": market_cap,
        "cash_q": cash_q,
        "total_debt_q": total_debt_q,
        "revenue_ttm": revenue_ttm,
        "ebitda_ttm": ebitda_ttm,
        "currency": currency,
        "asof_income": asof_income,
        "asof_balance": asof_balance,
    }

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("tickers", nargs="*", help="Tickers (default: CRM DDOG SNOW NET MDB)")
    p.add_argument("--out", default=None, help="Output CSV path (optional)")
    args = p.parse_args(argv)

    tickers = args.tickers or DEF_TICKERS
    rows = []
    for tk in tickers:
        try:
            row = fetch_one(tk)
            # Light warning if missing critical fields
            if row["shares_out"] is None:
                print(f"[warn] {tk}: shares_out missing")
            if row["market_cap"] is None:
                print(f"[warn] {tk}: market_cap missing")
            rows.append(row)
        except Exception as e:
            rows.append({"ticker": tk, "error": str(e)})

    df = pd.DataFrame(rows)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = pathlib.Path(args.out) if args.out else OUTDIR / f"comp_raw_{dt.datetime.now():%Y%m%d}.csv"
    df.to_csv(out, index=False)
    print(f"Wrote: {out}")

if __name__ == "__main__":
    sys.exit(main())
