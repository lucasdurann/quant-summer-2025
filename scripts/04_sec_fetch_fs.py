#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sec_download_fs.py
──────────────────
Fetch the latest 10-K for each ticker from the SEC, download an Excel with
the financial statements (native .xlsx if present; otherwise via ixviewer export),
and write tidy CSVs for Income, Balance Sheet, and Cash Flow.

Outputs (per ticker):
  data/comps/raw/<TICKER>_<FY>_Financial_Report.xlsx
  data/comps/raw/<TICKER>_<FY>_income.csv
  data/comps/raw/<TICKER>_<FY>_balance.csv
  data/comps/raw/<TICKER>_<FY>_cashflow.csv
"""

from __future__ import annotations
import os, time, re, urllib.parse, pathlib
from typing import Dict, List, Optional
import requests
import pandas as pd

# ─────────────────────────── Config ─────────────────────────── #
TICKERS = ["CRM", "DDOG", "SNOW"]  # edit list as needed
SEC_EMAIL = os.getenv("SEC_EMAIL") or "your.name+sec@example.com"

ROOT   = pathlib.Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "data" / "raw_sec_fs"
OUTDIR.mkdir(parents=True, exist_ok=True)

# Per-domain headers (do NOT pin Host incorrectly)
COMMON_HDRS = {"User-Agent": f"ValuationProject ({SEC_EMAIL})", "Accept-Encoding": "gzip, deflate"}
WWW_HDRS  = COMMON_HDRS.copy()   # www.sec.gov (ixviewer + /Archives/…/index.json)
DATA_HDRS = COMMON_HDRS.copy()   # data.sec.gov (submissions)

SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
DIR_INDEX   = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/index.json"
IX_DOC      = "https://www.sec.gov/ixviewer/doc?action=export&format=excel&source=content&doc={path}"
IX_URL      = "https://www.sec.gov/ixviewer/doc?action=export&format=excel&source=content&url={path}"

# ───────────────────────── HTTP helpers ─────────────────────── #

def _get(url: str, headers: Dict[str, str], timeout: int = 40, tries: int = 4):
    delay = 0.6
    for i in range(tries):
        r = requests.get(url, headers=headers, timeout=timeout, stream=False)
        if r.status_code in (429, 403) and i < tries - 1:
            time.sleep(delay); delay *= 1.7
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()  # pragma: no cover

def get_json(url: str, headers: Dict[str, str]):
    return _get(url, headers=headers).json()

# ───────────────────────── SEC utilities ────────────────────── #

def get_cik_map() -> Dict[str, str]:
    """Ticker -> zero-padded CIK string."""
    m = get_json("https://www.sec.gov/files/company_tickers.json", DATA_HDRS)
    return {row["ticker"].upper(): f'{int(row["cik_str"]):010d}' for row in m.values()}

def safe_get(rec: dict, field: str, idx: int):
    arr = rec.get(field, [])
    try:
        return arr[idx]
    except Exception:
        return None

def latest_10k(cik: str) -> Dict[str, str]:
    """Return metadata for the most recent 10-K (skip 10-K/A)."""
    rec = get_json(SUBMISSIONS.format(cik=cik), DATA_HDRS)["filings"]["recent"]
    for i, form in enumerate(rec.get("form", [])):
        if form != "10-K":
            continue
        acc_raw = safe_get(rec, "accessionNumber", i)
        primary = safe_get(rec, "primaryDocument", i)
        filing  = safe_get(rec, "filingDate", i)
        report  = safe_get(rec, "reportDate", i)
        fy      = safe_get(rec, "fy", i)
        if not acc_raw or not primary or not filing:
            continue
        acc = acc_raw.replace("-", "")
        rel = f"/Archives/edgar/data/{int(cik)}/{acc}/{primary}"
        year = str(fy) if fy else (report[:4] if report else filing[:4])
        return {"accession_raw": acc_raw, "accession": acc, "primary_doc": primary,
                "filing_date": filing, "report_date": report, "fy": year, "path_for_ix": rel}
    raise RuntimeError(f"No 10-K found or rows incomplete for CIK {cik}")

def find_attached_xlsx(cik: str, acc: str) -> Optional[str]:
    """Return filename of a native .xlsx attached to the filing directory, if any."""
    idx = get_json(DIR_INDEX.format(cik=int(cik), acc=acc), WWW_HDRS)
    items = idx.get("directory", {}).get("item", []) or []
    # Prefer obvious names; otherwise any .xlsx
    preferred = [it["name"] for it in items if it["name"].lower() in (
        "financial_report.xlsx", "Financial_Report.xlsx"
    )]
    if preferred:
        return preferred[0]
    xlsxs = [it["name"] for it in items if it["name"].lower().endswith(".xlsx")]
    return xlsxs[0] if xlsxs else None

def download_excel(cik: str, meta: dict, out_xlsx: pathlib.Path) -> None:
    """Download Excel for the filing: try native .xlsx first, then ixviewer export.
       Verify we didn't get an HTML error page."""
    def _save(resp):
        # guard: sometimes SEC returns HTML with 200
        ctype = resp.headers.get("Content-Type","").lower()
        if "html" in ctype:
            raise RuntimeError("Got HTML instead of Excel from SEC")
        out_xlsx.write_bytes(resp.content)

    # 1) Try native .xlsx inside the filing directory
    fname = find_attached_xlsx(cik, meta["accession"])
    if fname:
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{meta['accession']}/{fname}"
        resp = _get(url, WWW_HDRS, timeout=90)
        _save(resp); return

    # 2) Try ixviewer export (doc=… first; then url=… fallback)
    rel = meta["path_for_ix"]
    q   = urllib.parse.quote(rel, safe="/")
    for template in (IX_DOC, IX_URL):
        url = template.format(path=q)
        try:
            resp = _get(url, WWW_HDRS, timeout=90)
            _save(resp); return
        except Exception:
            continue
    raise RuntimeError(f"Excel export not available for {rel}")

# ───────────────────── Parsing & cleaning ───────────────────── #

def _find_sheet_name(all_names: List[str], candidates: List[str]) -> Optional[str]:
    low = [n.lower() for n in all_names]
    for cand in candidates:
        toks = cand.lower().split()
        for i, nm in enumerate(low):
            if all(t in nm for t in toks):
                return all_names[i]
    return None

def _clean_statement(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
    df = df.rename(columns={df.columns[0]: "LineItem"})
    # strip annotations like "(Audited)" in headers
    cols = ["LineItem"] + [re.sub(r"\s*\(.*?\)", "", str(c)).strip() for c in df.columns[1:]]
    df.columns = cols
    # coerce numerics for period columns
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # drop rows with all-NaN numeric cells
    df = df.dropna(subset=df.columns[1:], how="all").reset_index(drop=True)
    return df

def _score_sheet_for_type(line_items: list[str], kind: str) -> int:
    li = " | ".join(line_items).lower()
    if kind == "income":
        keys = [
            "revenue", "sales", "gross profit", "cost of revenue",
            "operating income", "operating loss",
            "net income", "net loss", "earnings per share"
        ]
    elif kind == "cashflow":
        keys = [
            "net cash provided by", "net cash used in operating activities",
            "cash flows from operating activities",
            "cash flows from investing activities",
            "cash flows from financing activities"
        ]
    else:  # balance
        keys = [
            "total assets", "total liabilities", "stockholders’ equity",
            "cash and cash equivalents", "accounts receivable", "long-term debt"
        ]
    return sum(1 for k in keys if k in li)

def parse_statements(xlsx_path: pathlib.Path) -> Dict[str, pd.DataFrame]:
    """Return dict with keys 'income', 'balance', 'cashflow' using name match
       and robust content-based fallback."""
    # choose engine explicitly
    engine = "openpyxl" if xlsx_path.suffix.lower() in {".xlsx", ".xlsm", ".xltx", ".xltm"} else "xlrd"
    xl = pd.ExcelFile(xlsx_path, engine=engine)
    names = xl.sheet_names

    # --- 1) try name-based match
    def _find_sheet_name(all_names, candidates):
        low = [n.lower() for n in all_names]
        for cand in candidates:
            toks = cand.lower().split()
            for i, nm in enumerate(low):
                if all(t in nm for t in toks):
                    return all_names[i]
        return None

    income_candidates  = [
        "consolidated statements of operations",
        "statements of operations",
        "statement of operations",
        "income statement",
        "statements of income",
        "statements of operations and comprehensive"
    ]
    balance_candidates = ["consolidated balance sheets", "balance sheet", "balance sheets"]
    cash_candidates    = [
        "consolidated statements of cash flows",
        "statements of cash flows", "cash flows", "cash flow"
    ]

    out: Dict[str, pd.DataFrame] = {}
    s_income  = _find_sheet_name(names, income_candidates)
    s_balance = _find_sheet_name(names, balance_candidates)
    s_cash    = _find_sheet_name(names, cash_candidates)

    if s_income:  out["income"]  = _clean_statement(xl.parse(s_income, header=0))
    if s_balance: out["balance"] = _clean_statement(xl.parse(s_balance, header=0))
    if s_cash:    out["cashflow"] = _clean_statement(xl.parse(s_cash, header=0))

    # --- 2) content-based fallback for any missing statement
    missing = [k for k in ("income", "balance", "cashflow") if k not in out]
    if missing:
        candidates = {}
        for sheet in names:
            df = _clean_statement(xl.parse(sheet, header=0))
            # consider only sheets with a text first column
            if "LineItem" not in df.columns or df.empty:
                continue
            line_items = df["LineItem"].astype(str).tolist()
            candidates[sheet] = {
                "df": df,
                "income":  _score_sheet_for_type(line_items, "income"),
                "balance": _score_sheet_for_type(line_items, "balance"),
                "cashflow":_score_sheet_for_type(line_items, "cashflow")
            }

        for kind in missing:
            best_sheet, best_score = None, -1
            for sh, meta in candidates.items():
                if meta[kind] > best_score:
                    best_sheet, best_score = sh, meta[kind]
            if best_sheet and best_score > 0:
                out[kind] = candidates[best_sheet]["df"]

    if not out:
        raise RuntimeError(f"No recognizable statement sheets in {xlsx_path.name}\nSheets: {names}")
    return out


# ─────────────────────────── Main ─────────────────────────── #

def main():
    print(f"Using SEC contact: {SEC_EMAIL}")
    cik_map = get_cik_map()

    for tkr in TICKERS:
        tkr = tkr.upper()
        cik = cik_map.get(tkr)
        if not cik:
            print(f"[WARN] CIK not found for {tkr}; skipping.")
            continue

        meta = latest_10k(cik)
        fy   = meta["fy"]
        out_xlsx = OUTDIR / f"{tkr}_{fy}_Financial_Report.xlsx"

        if not out_xlsx.exists():
            print(f"[{tkr}] Downloading Excel for 10-K {meta['accession_raw']} …")
            download_excel(cik, meta, out_xlsx)
            time.sleep(0.4)  # be polite to SEC

        print(f"[{tkr}] Parsing statements …")
        stmts = parse_statements(out_xlsx)
        for key, df in stmts.items():
            out_csv = OUTDIR / f"{tkr}_{fy}_{key}.csv"
            df.to_csv(out_csv, index=False)
            print(f"  • wrote {out_csv.name}  ({df.shape[0]} rows × {df.shape[1]} cols)")

    print(f"\nDone. Files saved to: {OUTDIR}")

if __name__ == "__main__":
    main()
