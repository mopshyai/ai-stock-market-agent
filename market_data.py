"""
Unified market data fetcher supporting yfinance (default) and Polygon.io.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

import pandas as pd
import requests
import yfinance as yf


INTERVAL_MAP: Dict[str, Tuple[int, str]] = {
    "1m": (1, "minute"),
    "2m": (2, "minute"),
    "5m": (5, "minute"),
    "15m": (15, "minute"),
    "30m": (30, "minute"),
    "45m": (45, "minute"),
    "1h": (1, "hour"),
    "2h": (2, "hour"),
    "4h": (4, "hour"),
    "1d": (1, "day"),
}


def _parse_period_days(period: str) -> int:
    """Convert yfinance-style period to days."""
    if not period:
        return 5
    try:
        value = int(period[:-1])
        unit = period[-1]
    except (ValueError, TypeError):
        return 5

    if unit == "d":
        return value
    if unit == "w":
        return value * 7
    if unit == "m":
        return value * 30
    if unit == "y":
        return value * 365
    return 5


def fetch_price_history(ticker: str, period: str, interval: str, provider: str = "yfinance",
                        data_cfg: Dict = None) -> pd.DataFrame:
    """
    Fetch OHLCV price history using the configured provider.

    provider: 'polygon' or 'yfinance'
    """
    data_cfg = data_cfg or {}
    provider = (provider or data_cfg.get("provider") or "yfinance").lower()

    if provider == "polygon":
        df = _fetch_polygon_prices(ticker, period, interval, data_cfg)
        if not df.empty:
            return df
        print(f"[POLYGON] Falling back to yfinance for {ticker}")

    return _fetch_yfinance_prices(ticker, period, interval)


def _fetch_yfinance_prices(ticker: str, period: str, interval: str) -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def _fetch_polygon_prices(ticker: str, period: str, interval: str, data_cfg: Dict) -> pd.DataFrame:
    api_key = os.getenv(data_cfg.get("polygon_api_key_env", "POLYGON_API_KEY"), data_cfg.get("polygon_api_key"))
    if not api_key:
        print("[POLYGON] API key not configured. Set POLYGON_API_KEY env var.")
        return pd.DataFrame()

    multiplier, timespan = INTERVAL_MAP.get(interval, (15, "minute"))
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=_parse_period_days(period))

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_dt:%Y-%m-%d}/{end_dt:%Y-%m-%d}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": api_key,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        print(f"[POLYGON ERROR] {ticker}: {exc}")
        return pd.DataFrame()

    results = payload.get("results") or []
    if not results:
        return pd.DataFrame()

    records = []
    for bar in results:
        ts = datetime.fromtimestamp(bar["t"] / 1000, tz=timezone.utc)
        records.append({
            "Datetime": ts,
            "Open": bar.get("o"),
            "High": bar.get("h"),
            "Low": bar.get("l"),
            "Close": bar.get("c"),
            "Volume": bar.get("v"),
        })

    df = pd.DataFrame.from_records(records)
    if df.empty:
        return df

    df.set_index("Datetime", inplace=True)
    # Convert timezone to naive for downstream compatibility
    df.index = df.index.tz_convert(None)
    return df
