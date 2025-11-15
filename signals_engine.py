"""
Technical signal engine with modular definitions.
"""
from dataclasses import dataclass
from typing import Callable, Dict, List

import pandas as pd


def _get_signal_cfg(cfg: Dict, name: str) -> Dict:
    return cfg.get("signals", {}).get(name, {})


def consolidating(df: pd.DataFrame, cfg: Dict) -> bool:
    s = _get_signal_cfg(cfg, "consolidation")
    lookback = s.get("lookback", 20)
    if len(df) < lookback:
        return False
    t = df.tail(lookback)
    return (
        t["bb_width"].mean() < s.get("bb_width_mean_max", 0.06) and
        t["atr_pct"].mean() < s.get("atr_pct_mean_max", 0.025) and
        t["adx"].mean() < s.get("adx_mean_max", 20)
    )


def buy_the_dip(df: pd.DataFrame, cfg: Dict) -> bool:
    s = _get_signal_cfg(cfg, "buy_the_dip")
    if df.empty:
        return False
    last = df.iloc[-1]
    if pd.isna(last["rsi"]) or pd.isna(last["bb_low"]):
        return False
    cond1 = last["rsi"] <= s.get("rsi_max", 35)
    cond2 = last["Close"] < last["bb_low"] if s.get("close_below_lower_bb", True) else True
    return cond1 and cond2


def breakout(df: pd.DataFrame, cfg: Dict) -> bool:
    s = _get_signal_cfg(cfg, "breakout")
    lookback = s.get("lookback", 20)
    if len(df) < lookback:
        return False
    last = df.iloc[-1]
    recent_high = df["High"].iloc[-lookback:-1].max()
    price_breakout = last["Close"] > recent_high
    adx_confirm = last["adx"] >= s.get("adx_min", 18)
    return price_breakout and adx_confirm


def volume_spike(df: pd.DataFrame, cfg: Dict) -> bool:
    s = _get_signal_cfg(cfg, "volume_spike")
    if df.empty:
        return False
    last = df.iloc[-1]
    if pd.isna(last["vol_ma_20"]) or last["vol_ma_20"] == 0:
        return False
    volume_ratio = last["Volume"] / last["vol_ma_20"]
    return volume_ratio >= s.get("volume_multiplier", 1.5)


def ema_bullish_alignment(df: pd.DataFrame, cfg: Dict) -> bool:
    if df.empty:
        return False
    last = df.iloc[-1]
    if pd.isna(last["ema_20"]) or pd.isna(last["ema_50"]) or pd.isna(last["ema_200"]):
        return False
    if not (last["ema_20"] > last["ema_50"] > last["ema_200"]):
        return False
    s = _get_signal_cfg(cfg, "ema_bullish")
    min_sep = s.get("min_separation_pct", 0.5) / 100
    sep1 = (last["ema_20"] - last["ema_50"]) / last["ema_50"]
    sep2 = (last["ema_50"] - last["ema_200"]) / last["ema_200"]
    return sep1 >= min_sep and sep2 >= min_sep


def macd_bullish_cross(df: pd.DataFrame, cfg: Dict) -> bool:
    if len(df) < 2 or "macd" not in df.columns or "macd_signal" not in df.columns:
        return False
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if any(pd.isna(val) for val in [last["macd"], last["macd_signal"], prev["macd"], prev["macd_signal"]]):
        return False
    crossed = prev["macd"] <= prev["macd_signal"] and last["macd"] > last["macd_signal"]
    if not crossed:
        return False
    s = _get_signal_cfg(cfg, "macd_bullish")
    hist_min = s.get("histogram_min", 0.0)
    hist_val = last.get("macd_hist", 0)
    return hist_val >= hist_min


def vwap_reclaim(df: pd.DataFrame, cfg: Dict) -> bool:
    if "vwap" not in df.columns or df.empty:
        return False
    s = _get_signal_cfg(cfg, "vwap_reclaim")
    lookback = max(s.get("lookback", 20), 2)
    pct = s.get("min_close_above_pct", 0.2) / 100
    recent = df.tail(lookback)
    last = recent.iloc[-1]
    if pd.isna(last["vwap"]):
        return False
    above = last["Close"] >= last["vwap"] * (1 + pct)
    prev_below = (recent.iloc[:-1]["Close"] < recent.iloc[:-1]["vwap"]).any()
    return above and prev_below


@dataclass(frozen=True)
class SignalDefinition:
    key: str
    label: str
    weight: int
    detector: Callable[[pd.DataFrame, Dict], bool]


SIGNAL_DEFINITIONS: List[SignalDefinition] = [
    SignalDefinition("Consolidating", "🟢 CONSOLIDATION", 1, consolidating),
    SignalDefinition("BuyDip", "📉 BUY THE DIP", 2, buy_the_dip),
    SignalDefinition("Breakout", "🚀 BREAKOUT", 3, breakout),
    SignalDefinition("VolSpike", "📈 VOLUME SPIKE", 1, volume_spike),
    SignalDefinition("EMABullish", "📐 EMA STACK", 1, ema_bullish_alignment),
    SignalDefinition("MACDBullish", "🎯 MACD BULLISH", 1, macd_bullish_cross),
    SignalDefinition("VWAPReclaim", "💧 VWAP RECLAIM", 1, vwap_reclaim),
]


def evaluate_signals(df: pd.DataFrame, cfg: Dict) -> Dict[str, bool]:
    results: Dict[str, bool] = {}
    for definition in SIGNAL_DEFINITIONS:
        try:
            results[definition.key] = bool(definition.detector(df, cfg))
        except Exception as exc:
            print(f"[SIGNAL ERROR] {definition.key}: {exc}")
            results[definition.key] = False
    return results
