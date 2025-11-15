"""
Fundamental analysis helpers for AI Stock Market Agent.

Fetches a lightweight set of metrics from yfinance, caches results to avoid
rate limits, scores companies, and produces trade recommendations when
combined with technical scores.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

import yfinance as yf


CACHE_DIR = Path(".cache")
CACHE_FILE = CACHE_DIR / "fundamentals_cache.json"
CACHE_TTL = 6 * 60 * 60  # 6 hours


def _load_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {}
    try:
        with CACHE_FILE.open("r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache: Dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with CACHE_FILE.open("w") as f:
        json.dump(cache, f)


def _sanitize(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


@dataclass
class Fundamentals:
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    revenue_growth_pct: Optional[float]
    profit_margin_pct: Optional[float]
    fundamental_score: int
    outlook: str
    reasons: str


def fetch_fundamentals(ticker: str) -> Fundamentals:
    """
    Fetch (and cache) fundamental metrics for a ticker.
    """
    cache = _load_cache()
    entry = cache.get(ticker.upper())
    now = time.time()

    if entry and now - entry.get("timestamp", 0) < CACHE_TTL:
        return Fundamentals(**entry["data"])

    info: Dict[str, Any] = {}
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception:
        info = {}

    market_cap = _sanitize(info.get("marketCap"))
    pe_ratio = _sanitize(info.get("trailingPE") or info.get("forwardPE"))
    revenue_growth_pct = None
    if info.get("revenueQuarterlyGrowth") is not None:
        revenue_growth_pct = _sanitize(info.get("revenueQuarterlyGrowth") * 100)
    profit_margin_pct = None
    if info.get("profitMargins") is not None:
        profit_margin_pct = _sanitize(info.get("profitMargins") * 100)

    fundamental_score, outlook, reasons = _score_fundamentals(
        market_cap, pe_ratio, revenue_growth_pct, profit_margin_pct
    )

    data = Fundamentals(
        market_cap=market_cap,
        pe_ratio=pe_ratio,
        revenue_growth_pct=revenue_growth_pct,
        profit_margin_pct=profit_margin_pct,
        fundamental_score=fundamental_score,
        outlook=outlook,
        reasons=reasons,
    )

    cache[ticker.upper()] = {
        "timestamp": now,
        "data": data.__dict__,
    }
    _save_cache(cache)
    return data


def _score_fundamentals(
    market_cap: Optional[float],
    pe_ratio: Optional[float],
    revenue_growth_pct: Optional[float],
    profit_margin_pct: Optional[float],
) -> (int, str, str):
    score = 0
    reasons = []

    if revenue_growth_pct is not None:
        if revenue_growth_pct >= 10:
            score += 1
            reasons.append(f"Rev growth {revenue_growth_pct:.1f}%")
        elif revenue_growth_pct < 0:
            score -= 1
            reasons.append("Revenue contracting")

    if profit_margin_pct is not None:
        if profit_margin_pct >= 10:
            score += 1
            reasons.append(f"Profit margin {profit_margin_pct:.1f}%")
        elif profit_margin_pct < 0:
            score -= 1
            reasons.append("Negative margin")

    if pe_ratio is not None:
        if 5 <= pe_ratio <= 40:
            score += 1
            reasons.append(f"P/E {pe_ratio:.1f}")
        elif pe_ratio > 60:
            score -= 1
            reasons.append("Expensive valuation")

    if market_cap and market_cap >= 5e9:
        score += 1
        reasons.append("Large-cap stability")

    # Clamp to keep weighting under control
    score = max(-2, min(score, 3))

    if score >= 3:
        outlook = "BULLISH"
    elif score >= 1:
        outlook = "POSITIVE"
    elif score >= 0:
        outlook = "NEUTRAL"
    else:
        outlook = "CAUTIOUS"

    return score, outlook, "; ".join(reasons)


def recommend_trade_action(technical_score: int, fundamental_score: int, trend: str) -> Dict[str, str]:
    """
    Combine technical and fundamental scores into a suggested action.
    """
    total_score = technical_score + fundamental_score

    if total_score >= 6 and technical_score >= 4:
        action = "BUY"
        reason = "High-probability setup with strong fundamentals"
    elif total_score >= 4:
        action = "WATCH"
        reason = "Good setup forming—wait for confirmation"
    else:
        action = "AVOID"
        reason = "Signal too weak right now"

    if trend == "DOWN" and action == "BUY":
        action = "WATCH"
        reason = "Technical score strong but trend is down"

    return {"action": action, "reason": reason, "total_score": total_score}
