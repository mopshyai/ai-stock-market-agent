"""
Interactive TradingView-style charts using Lightweight Charts
"""
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts


def create_interactive_chart(df: pd.DataFrame, ticker: str, height: int = 600):
    """
    Create an interactive TradingView-style chart using Lightweight Charts

    Args:
        df: DataFrame with OHLCV data and datetime index
        ticker: Stock ticker symbol
        height: Chart height in pixels

    Returns:
        Chart configuration dict for renderLightweightCharts
    """

    # Prepare candlestick data
    candle_data = []
    for idx, row in df.iterrows():
        candle_data.append({
            'time': int(idx.timestamp()),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close']),
        })

    # Prepare volume data
    volume_data = []
    for idx, row in df.iterrows():
        # Color volume bars based on candle direction
        color = '#26a69a' if row['Close'] >= row['Open'] else '#ef5350'
        volume_data.append({
            'time': int(idx.timestamp()),
            'value': float(row['Volume']),
            'color': color,
        })

    # Prepare MA20 line
    ma20_data = []
    if 'ema_20' in df.columns:
        for idx, row in df.iterrows():
            if pd.notna(row['ema_20']):
                ma20_data.append({
                    'time': int(idx.timestamp()),
                    'value': float(row['ema_20']),
                })

    # Prepare MA50 line
    ma50_data = []
    if 'ema_50' in df.columns:
        for idx, row in df.iterrows():
            if pd.notna(row['ema_50']):
                ma50_data.append({
                    'time': int(idx.timestamp()),
                    'value': float(row['ema_50']),
                })

    # Chart configuration
    chart_options = {
        "layout": {
            "background": {"type": "solid", "color": "#131722"},
            "textColor": "#d1d4dc",
        },
        "grid": {
            "vertLines": {"color": "#2a2e39"},
            "horzLines": {"color": "#2a2e39"},
        },
        "crosshair": {
            "mode": 0,  # Normal crosshair
        },
        "timeScale": {
            "borderColor": "#2a2e39",
            "timeVisible": True,
            "secondsVisible": False,
        },
        "watermark": {
            "visible": True,
            "fontSize": 48,
            "horzAlign": 'center',
            "vertAlign": 'center',
            "color": 'rgba(209, 212, 220, 0.1)',
            "text": ticker,
        },
    }

    # Series configuration
    series_config = [
        {
            "type": "Candlestick",
            "data": candle_data,
            "options": {
                "upColor": "#26a69a",
                "downColor": "#ef5350",
                "borderVisible": False,
                "wickUpColor": "#26a69a",
                "wickDownColor": "#ef5350",
            }
        },
    ]

    # Add MA20 if available
    if ma20_data:
        series_config.append({
            "type": "Line",
            "data": ma20_data,
            "options": {
                "color": "#2962FF",
                "lineWidth": 2,
                "title": "EMA 20",
            }
        })

    # Add MA50 if available
    if ma50_data:
        series_config.append({
            "type": "Line",
            "data": ma50_data,
            "options": {
                "color": "#F23645",
                "lineWidth": 2,
                "title": "EMA 50",
            }
        })

    # Add volume histogram
    series_config.append({
        "type": "Histogram",
        "data": volume_data,
        "options": {
            "priceFormat": {
                "type": "volume",
            },
            "priceScaleId": "volume",
        },
        "priceScale": {
            "scaleMargins": {
                "top": 0.8,
                "bottom": 0,
            },
        }
    })

    return renderLightweightCharts([
        {
            "chart": chart_options,
            "series": series_config
        }
    ], f'chart_{ticker}')
