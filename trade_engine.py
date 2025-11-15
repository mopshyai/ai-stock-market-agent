
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from database_postgres import (
    create_trade, get_pending_trades, get_open_trades,
    update_trade_status, close_trade, get_trade_summary
)

"""
Trade Engine - Converts signals to trades and manages trade lifecycle
"""


def calculate_trade_levels(signal_data: Dict, cfg: dict) -> Dict:
    """
    Calculate entry, stop loss, and take profit levels from signal data

    Logic:
    - Entry: Current price (for BUY-DIP) or breakout level
    - Stop Loss: Based on ATR or fixed % below entry
    - TP1: 1R (1x risk)
    - TP2: 2R (2x risk)
    """
    ticker = signal_data.get('Ticker')
    current_price = signal_data.get('Close')
    atr_pct = signal_data.get('ATR%', 2.0) / 100  # Convert to decimal

    # Risk settings from config (or defaults)
    risk_cfg = cfg.get('risk_management', {})
    stop_loss_atr_mult = risk_cfg.get('stop_loss_atr_multiplier', 1.5)
    use_fixed_stop = risk_cfg.get('use_fixed_stop_pct', False)
    fixed_stop_pct = risk_cfg.get('fixed_stop_pct', 2.0) / 100

    # Calculate stop loss
    if use_fixed_stop:
        stop_distance = current_price * fixed_stop_pct
    else:
        stop_distance = current_price * atr_pct * stop_loss_atr_mult

    stop_loss = current_price - stop_distance

    # Calculate take profit levels (R-multiple based)
    risk_per_share = stop_distance
    tp1 = current_price + (risk_per_share * 1.0)  # 1R
    tp2 = current_price + (risk_per_share * 2.0)  # 2R

    # Build trade plan
    entry_price = current_price

    # Generate trade notes
    signals = []
    if signal_data.get('Consolidating'):
        signals.append('CONS')
    if signal_data.get('BuyDip'):
        signals.append('BUY-DIP')
    if signal_data.get('Breakout'):
        signals.append('BREAKOUT')
    if signal_data.get('VolSpike'):
        signals.append('VOL')

    trend = signal_data.get('Trend', 'CHOPPY')
    score = signal_data.get('Score', 0)

    notes = f"{' + '.join(signals)} | {trend} TREND | Score: {score}"

    return {
        'ticker': ticker,
        'entry_price': round(entry_price, 2),
        'stop_loss': round(stop_loss, 2),
        'tp1': round(tp1, 2),
        'tp2': round(tp2, 2),
        'risk_per_share': round(risk_per_share, 2),
        'notes': notes
    }


def signal_to_trade(signal_data: Dict, signal_id: int, cfg: dict) -> Optional[int]:
    """
    Convert a signal to a pending trade
    Returns trade_id if successful
    """
    # Only create trades for signals with minimum score
    min_score = cfg.get('risk_management', {}).get('min_signal_score', 3)
    if signal_data.get('Score', 0) < min_score:
        print(f"[SKIP] {signal_data.get('Ticker')} - Score too low")
        return None

    # Calculate trade levels
    trade_plan = calculate_trade_levels(signal_data, cfg)

    # Calculate risk amount (fixed $ or % of capital)
    risk_cfg = cfg.get('risk_management', {})
    risk_per_trade = risk_cfg.get('risk_per_trade_dollars', 100)

    # Create pending trade
    trade_id = create_trade(
        signal_id=signal_id,
        ticker=trade_plan['ticker'],
        entry_price=trade_plan['entry_price'],
        stop_loss=trade_plan['stop_loss'],
        tp1=trade_plan['tp1'],
        tp2=trade_plan['tp2'],
        risk_amount=risk_per_trade,
        notes=trade_plan['notes']
    )

    return trade_id


def get_current_price(ticker: str) -> Optional[float]:
    """Get current price for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d', interval='1m')

        if data.empty:
            return None

        return float(data['Close'].iloc[-1])

    except Exception as e:
        print(f"[ERROR] Failed to get price for {ticker}: {e}")
        return None


def check_pending_entries(cfg: dict) -> List[Dict]:
    """
    Check all pending trades to see if entry price has been hit
    Returns list of newly opened trades
    """
    pending = get_pending_trades()

    if pending.empty:
        return []

    opened_trades = []

    for _, trade in pending.iterrows():
        trade_id = trade['trade_id']
        ticker = trade['ticker']
        entry_price = trade['entry_price']

        # Get current price
        current_price = get_current_price(ticker)

        if current_price is None:
            continue

        # Check if price crossed entry level (assuming BUY trades)
        # For BUY: entry is triggered when price >= entry_price
        if current_price >= entry_price:
            # Activate trade
            update_trade_status(trade_id, 'OPEN', current_price)

            opened_trades.append({
                'trade_id': trade_id,
                'ticker': ticker,
                'entry_price': entry_price,
                'actual_entry': current_price,
                'stop_loss': trade['stop_loss'],
                'tp1': trade['tp1'],
                'tp2': trade['tp2']
            })

            print(f"▶️  ENTRY: {ticker} @ {current_price:.2f}")

    return opened_trades


def monitor_open_trades(cfg: dict) -> List[Dict]:
    """
    Monitor all open trades for stop loss or take profit hits
    Returns list of closed trades
    """
    open_trades = get_open_trades()

    if open_trades.empty:
        return []

    closed_trades = []

    for _, trade in open_trades.iterrows():
        trade_id = trade['trade_id']
        ticker = trade['ticker']
        entry_price = trade['entry_price']
        stop_loss = trade['stop_loss']
        tp1 = trade['tp1']
        tp2 = trade['tp2']

        # Get current price
        current_price = get_current_price(ticker)

        if current_price is None:
            continue

        # Check exit conditions
        exit_reason = None
        exit_price = current_price

        # Check STOP LOSS
        if current_price <= stop_loss:
            exit_reason = 'STOP'
            exit_price = stop_loss

        # Check TP2 (check higher level first)
        elif current_price >= tp2:
            exit_reason = 'TP2'
            exit_price = tp2

        # Check TP1
        elif current_price >= tp1:
            exit_reason = 'TP1'
            exit_price = tp1

        # If any exit condition met, close the trade
        if exit_reason:
            result = close_trade(trade_id, exit_price, exit_reason)

            if result:
                closed_trades.append(result)

                # Emoji for result
                if exit_reason == 'STOP':
                    print(f"❌ STOP: {ticker} @ {exit_price:.2f} | {result['r_multiple']}R")
                elif exit_reason == 'TP1':
                    print(f"✅ TP1: {ticker} @ {exit_price:.2f} | {result['r_multiple']}R")
                elif exit_reason == 'TP2':
                    print(f"🎯 TP2: {ticker} @ {exit_price:.2f} | {result['r_multiple']}R")

        else:
            # No exit yet, just update current price
            update_trade_status(trade_id, 'OPEN', current_price)

    return closed_trades


def check_daily_risk_limit(cfg: dict) -> Tuple[bool, float]:
    """
    Check if daily loss limit has been hit
    Returns (can_trade, current_daily_r)
    """
    summary = get_trade_summary(days=1)  # Today only

    risk_cfg = cfg.get('risk_management', {})
    max_daily_loss_r = risk_cfg.get('max_daily_loss_r', 3.0)

    # Calculate total R for today
    # This would need trades closed today
    # For now, use avg_r * closed_count as approximation
    daily_r = summary['avg_r'] * summary['closed']

    can_trade = daily_r > -max_daily_loss_r

    return can_trade, daily_r


def run_trade_monitor_cycle(cfg: dict) -> Dict:
    """
    Run one complete monitoring cycle:
    1. Check pending entries
    2. Monitor open trades
    3. Check risk limits

    Returns summary of actions taken
    """
    print("\n" + "="*50)
    print(f"🤖 TRADE MONITOR | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    # Check risk limits first
    can_trade, daily_r = check_daily_risk_limit(cfg)

    if not can_trade:
        print(f"⚠️  DAILY LOSS LIMIT HIT: {daily_r:.2f}R")
        print("🛑 New entries disabled for today")
        return {
            'status': 'RISK_LIMIT_HIT',
            'daily_r': daily_r
        }

    # Check for new entries
    new_entries = check_pending_entries(cfg)

    # Monitor open trades
    closed = monitor_open_trades(cfg)

    # Get current summary
    summary = get_trade_summary(days=1)

    print("\n📊 TRADE SUMMARY:")
    print(f"   Open: {summary['open']} | Pending: {summary['pending']} | Closed Today: {summary['closed']}")
    if summary['closed'] > 0:
        print(f"   Win Rate: {summary['win_rate']}% | Avg R: {summary['avg_r']}R | P&L: ${summary['total_pnl']}")

    return {
        'status': 'OK',
        'new_entries': len(new_entries),
        'new_exits': len(closed),
        'entries': new_entries,
        'exits': closed,
        'summary': summary
    }


if __name__ == "__main__":
    import yaml

    # Load config
    cfg = yaml.safe_load(open("config.yaml", "r"))

    # Run one monitoring cycle
    result = run_trade_monitor_cycle(cfg)

    print("\n✅ Monitor cycle complete")
