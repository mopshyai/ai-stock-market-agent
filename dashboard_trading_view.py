"""
Enhanced dashboard view functions for trading guidance
Shows clear BUY/WATCH/AVOID recommendations with price targets
"""

import streamlit as st


def get_action_color_and_emoji(action: str) -> tuple:
    """Return color and emoji for action type"""
    action_styles = {
        'BUY': ('#00D084', '🟢'),           # Green
        'WATCH': ('#FFA500', '👀'),          # Orange
        'AVOID': ('#FF6B6B', '⛔'),          # Red
        'TAKE_PROFIT': ('#00D084', '💰'),    # Green
        'TRAIL_STOP': ('#FFD93D', '⚡'),     # Yellow
    }
    return action_styles.get(action, ('#888888', '⚪'))


def display_stock_card_enhanced(row):
    """
    Display enhanced stock card with clear trading guidance
    Shows: Action, Potential Moves, Entry/Stop/Targets
    """
    ticker = row.get('Ticker', 'N/A')
    action = row.get('Action', 'WATCH')
    score = row.get('Score', 0)
    close = row.get('Close', 0)
    trend = row.get('Trend', 'CHOPPY')
    signals = row.get('Signals', 'None')
    timeframe_label = row.get('TimeframeLabel', 'intraday')
    action_reason = row.get('ActionReason', '')

    # Price levels
    entry_price = row.get('EntryPrice', close)
    stop_loss = row.get('StopLossPrice', 0)
    tp1 = row.get('TakeProfit1', 0)
    tp2 = row.get('TakeProfit2', 0)

    # Potential moves
    pot_up_1h = row.get('PotentialUp1h', 0)
    pot_down_1h = row.get('PotentialDown1h', 0)
    pot_up_1d = row.get('PotentialUp1d', 0)
    pot_down_1d = row.get('PotentialDown1d', 0)
    pot_up_7d = row.get('PotentialUp7d', 0)
    pot_down_7d = row.get('PotentialDown7d', 0)

    # Get styling
    color, emoji = get_action_color_and_emoji(action)

    with st.container():
        st.markdown("---")

        # Header row
        col_header1, col_header2, col_header3 = st.columns([2, 2, 3])

        with col_header1:
            st.markdown(f"## {ticker}")
            st.caption(f"${close:.2f}")

        with col_header2:
            st.markdown(
                f'<div style="background:{color};color:white;padding:10px;border-radius:8px;text-align:center;font-size:24px;font-weight:bold">'
                f'{emoji} {action}'
                f'</div>',
                unsafe_allow_html=True
            )
            st.caption(f"Timeframe: {timeframe_label}")

        with col_header3:
            st.metric("Score", f"{score}/10", delta=None)
            st.caption(f"Trend: {trend} | Signals: {signals}")

        # Action reason (clear explanation)
        st.info(f"📌 **{action_reason}**")

        # Details tabs
        tab1, tab2, tab3 = st.tabs(["📊 Price Targets", "⏱️ Potential Moves", "📈 Indicators"])

        with tab1:
            col_levels1, col_levels2 = st.columns(2)

            with col_levels1:
                st.markdown("### Entry & Risk")
                st.metric("Entry", f"${entry_price:.2f}")
                st.metric("Stop Loss", f"${stop_loss:.2f}",
                         delta=f"-{((entry_price - stop_loss) / entry_price * 100):.2f}%",
                         delta_color="inverse")

            with col_levels2:
                st.markdown("### Take Profit Targets")
                st.metric("TP1 (Conservative)", f"${tp1:.2f}",
                         delta=f"+{((tp1 - entry_price) / entry_price * 100):.2f}%")
                st.metric("TP2 (Aggressive)", f"${tp2:.2f}",
                         delta=f"+{((tp2 - entry_price) / entry_price * 100):.2f}%")

        with tab2:
            st.markdown("### Expected Move Ranges")

            col_tf1, col_tf2, col_tf3 = st.columns(3)

            with col_tf1:
                st.markdown("**1 Hour**")
                st.success(f"↑ +{pot_up_1h:.2f}%")
                st.error(f"↓ -{pot_down_1h:.2f}%")

            with col_tf2:
                st.markdown("**1 Day**")
                st.success(f"↑ +{pot_up_1d:.2f}%")
                st.error(f"↓ -{pot_down_1d:.2f}%")

            with col_tf3:
                st.markdown("**7 Days**")
                st.success(f"↑ +{pot_up_7d:.2f}%")
                st.error(f"↓ -{pot_down_7d:.2f}%")

            st.caption("💡 These are volatility-based estimates, not predictions.")

        with tab3:
            indicators_df = {
                'Indicator': ['RSI', 'ADX', 'BB Width', 'ATR%'],
                'Value': [
                    f"{row.get('RSI', 0):.1f}",
                    f"{row.get('ADX', 0):.1f}",
                    f"{row.get('BBWidth_pct', 0):.2f}%",
                    f"{row.get('ATR%', 0):.2f}%"
                ]
            }
            st.table(indicators_df)


def display_action_summary(df):
    """Display summary of actions across all stocks"""
    if df.empty:
        return

    # Count actions
    action_counts = df['Action'].value_counts().to_dict()

    st.markdown("### 📊 Market Overview")

    cols = st.columns(5)

    # BUY
    with cols[0]:
        buy_count = action_counts.get('BUY', 0)
        st.metric("🟢 BUY", buy_count)

    # WATCH
    with cols[1]:
        watch_count = action_counts.get('WATCH', 0)
        st.metric("👀 WATCH", watch_count)

    # AVOID
    with cols[2]:
        avoid_count = action_counts.get('AVOID', 0)
        st.metric("⛔ AVOID", avoid_count)

    # TAKE_PROFIT
    with cols[3]:
        tp_count = action_counts.get('TAKE_PROFIT', 0)
        st.metric("💰 TAKE PROFIT", tp_count)

    # TRAIL_STOP
    with cols[4]:
        trail_count = action_counts.get('TRAIL_STOP', 0)
        st.metric("⚡ TRAIL STOP", trail_count)


def display_disclaimer():
    """Display educational disclaimer"""
    st.markdown("---")
    st.warning(
        "⚠️ **DISCLAIMER**: This tool is for educational purposes only. "
        "Not financial advice. Always do your own research before making trading decisions. "
        "Past performance does not guarantee future results. Trading involves risk."
    )
