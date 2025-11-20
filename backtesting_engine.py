#!/usr/bin/env python3
"""
BACKTESTING ENGINE
Historical signal replay and performance simulation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from database import get_db_connection, format_sql


class BacktestEngine:
    """
    Backtest historical signals to measure performance
    """
    
    def __init__(self, initial_capital: float = 10000.0, risk_per_trade_pct: float = 1.0):
        """
        Args:
            initial_capital: Starting capital for backtest
            risk_per_trade_pct: % of capital to risk per trade
        """
        self.initial_capital = initial_capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.trades: List[Dict] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        
    def get_historical_signals(self, days: int = 90, min_score: int = 3) -> pd.DataFrame:
        """
        Fetch historical signals from database
        """
        conn = get_db_connection()
        
        query = format_sql("""
            SELECT 
                signal_id,
                ticker,
                signal_date,
                score,
                trend,
                price_at_signal,
                rsi,
                adx,
                atr_pct,
                bb_width_pct,
                consolidating,
                buy_dip,
                breakout,
                vol_spike
            FROM signals
            WHERE signal_date >= date('now', '-' || ? || ' days')
            AND score >= ?
            ORDER BY signal_date ASC
        """)
        
        df = pd.read_sql_query(query, conn, params=(days, min_score))
        conn.close()
        
        return df
    
    def simulate_trade(self, signal: pd.Series, holding_days: int = 5) -> Dict:
        """
        Simulate a single trade based on signal
        
        Args:
            signal: Signal data row
            holding_days: Number of days to hold position
            
        Returns:
            Dict with trade results
        """
        ticker = signal['ticker']
        entry_date = pd.to_datetime(signal['signal_date'])
        entry_price = signal['price_at_signal']
        
        # Get historical price data
        try:
            end_date = entry_date + timedelta(days=holding_days + 5)
            stock = yf.Ticker(ticker)
            hist = stock.history(start=entry_date, end=end_date)
            
            if len(hist) < 2:
                return None
            
            # Calculate stop loss and take profit
            atr_pct = signal.get('atr_pct', 0.02)
            stop_loss = entry_price * (1 - (atr_pct * 1.5))  # 1.5 ATR stop
            take_profit_1 = entry_price * (1 + (atr_pct * 1.5))  # 1R
            take_profit_2 = entry_price * (1 + (atr_pct * 3.0))  # 2R
            
            # Simulate trade execution
            exit_price = None
            exit_reason = None
            exit_date = None
            
            for idx, (date, row) in enumerate(hist.iterrows()):
                if idx == 0:
                    continue  # Skip entry day
                
                # Check stop loss
                if row['Low'] <= stop_loss:
                    exit_price = stop_loss
                    exit_reason = 'STOP_LOSS'
                    exit_date = date
                    break
                
                # Check take profit
                if row['High'] >= take_profit_2:
                    exit_price = take_profit_2
                    exit_reason = 'TP2'
                    exit_date = date
                    break
                elif row['High'] >= take_profit_1:
                    exit_price = take_profit_1
                    exit_reason = 'TP1'
                    exit_date = date
                    break
                
                # Max holding period
                if idx >= holding_days:
                    exit_price = row['Close']
                    exit_reason = 'TIME_EXIT'
                    exit_date = date
                    break
            
            # If no exit triggered, use last close
            if exit_price is None:
                exit_price = hist.iloc[-1]['Close']
                exit_reason = 'TIME_EXIT'
                exit_date = hist.index[-1]
            
            # Calculate P/L
            risk_amount = self.initial_capital * (self.risk_per_trade_pct / 100)
            position_size = risk_amount / (entry_price - stop_loss)
            pnl = (exit_price - entry_price) * position_size
            r_multiple = (exit_price - entry_price) / (entry_price - stop_loss)
            
            return {
                'signal_id': signal['signal_id'],
                'ticker': ticker,
                'entry_date': entry_date,
                'entry_price': entry_price,
                'exit_date': exit_date,
                'exit_price': exit_price,
                'exit_reason': exit_reason,
                'stop_loss': stop_loss,
                'tp1': take_profit_1,
                'tp2': take_profit_2,
                'position_size': position_size,
                'pnl': pnl,
                'r_multiple': r_multiple,
                'score': signal['score'],
                'holding_days': (exit_date - entry_date).days
            }
            
        except Exception as e:
            print(f"Error simulating trade for {ticker}: {e}")
            return None
    
    def run_backtest(self, days: int = 90, min_score: int = 3, holding_days: int = 5) -> Dict:
        """
        Run backtest on historical signals
        
        Returns:
            Dict with backtest results and statistics
        """
        print(f"🔄 Running backtest: {days} days, min score {min_score}")
        
        # Get signals
        signals_df = self.get_historical_signals(days, min_score)
        print(f"📊 Found {len(signals_df)} signals to backtest")
        
        if len(signals_df) == 0:
            return {
                'total_trades': 0,
                'error': 'No signals found for backtest period'
            }
        
        # Simulate each trade
        self.trades = []
        capital = self.initial_capital
        
        for idx, signal in signals_df.iterrows():
            trade_result = self.simulate_trade(signal, holding_days)
            
            if trade_result:
                self.trades.append(trade_result)
                capital += trade_result['pnl']
                self.equity_curve.append((trade_result['exit_date'], capital))
                
                # Progress
                if (idx + 1) % 10 == 0:
                    print(f"  Processed {idx + 1}/{len(signals_df)} signals...")
        
        # Calculate statistics
        trades_df = pd.DataFrame(self.trades)
        
        if len(trades_df) == 0:
            return {
                'total_trades': 0,
                'error': 'No valid trades executed'
            }
        
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] <= 0]
        
        stats = {
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(trades_df) * 100) if len(trades_df) > 0 else 0,
            'total_pnl': trades_df['pnl'].sum(),
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'largest_win': trades_df['pnl'].max(),
            'largest_loss': trades_df['pnl'].min(),
            'avg_r_multiple': trades_df['r_multiple'].mean(),
            'final_capital': capital,
            'total_return_pct': ((capital - self.initial_capital) / self.initial_capital * 100),
            'avg_holding_days': trades_df['holding_days'].mean(),
            'trades_data': trades_df,
            'equity_curve': self.equity_curve
        }
        
        return stats
    
    def print_results(self, stats: Dict):
        """Print backtest results"""
        print("\n" + "="*60)
        print("📈 BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Capital: ${stats['final_capital']:,.2f}")
        print(f"Total Return: {stats['total_return_pct']:.2f}%")
        print(f"Total P/L: ${stats['total_pnl']:,.2f}")
        print()
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Winning Trades: {stats['winning_trades']}")
        print(f"Losing Trades: {stats['losing_trades']}")
        print(f"Win Rate: {stats['win_rate']:.2f}%")
        print()
        print(f"Average R-Multiple: {stats['avg_r_multiple']:.2f}R")
        print(f"Average Win: ${stats['avg_win']:,.2f}")
        print(f"Average Loss: ${stats['avg_loss']:,.2f}")
        print(f"Largest Win: ${stats['largest_win']:,.2f}")
        print(f"Largest Loss: ${stats['largest_loss']:,.2f}")
        print(f"Average Holding Period: {stats['avg_holding_days']:.1f} days")
        print("="*60)


if __name__ == "__main__":
    print("🚀 StockGenie Backtesting Engine\n")
    
    # Run backtest
    engine = BacktestEngine(initial_capital=10000, risk_per_trade_pct=1.0)
    results = engine.run_backtest(days=90, min_score=3, holding_days=5)
    
    # Print results
    if 'error' not in results:
        engine.print_results(results)
        
        # Show top 5 trades
        print("\n🏆 Top 5 Trades by P/L:")
        top_trades = results['trades_data'].nlargest(5, 'pnl')[
            ['ticker', 'entry_date', 'exit_date', 'pnl', 'r_multiple', 'exit_reason']
        ]
        print(top_trades.to_string(index=False))
    else:
        print(f"⚠️  Error: {results['error']}")
