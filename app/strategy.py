import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime


def calculate_moving_average(prices: List[float], window: int) -> List[float]:
    """Calculate simple moving average"""
    if len(prices) < window:
        return [np.nan] * len(prices)

    df = pd.DataFrame({'price': prices})
    ma = df['price'].rolling(window=window).mean()
    return ma.tolist()


def generate_signals(short_ma: List[float], long_ma: List[float]) -> List[str]:
    """Generate buy/sell signals based on moving average crossover"""
    signals = []

    for i in range(len(short_ma)):
        if i == 0 or pd.isna(short_ma[i]) or pd.isna(long_ma[i]):
            signals.append('HOLD')
        elif pd.isna(short_ma[i-1]) or pd.isna(long_ma[i-1]):
            signals.append('HOLD')
        elif short_ma[i-1] <= long_ma[i-1] and short_ma[i] > long_ma[i]:
            signals.append('BUY')
        elif short_ma[i-1] >= long_ma[i-1] and short_ma[i] < long_ma[i]:
            signals.append('SELL')
        else:
            signals.append('HOLD')

    return signals


def calculate_strategy_performance(
    data: List[Dict],
    short_window: int = 20,
    long_window: int = 50
) -> Dict:
    """Calculate performance of moving average crossover strategy"""
    if len(data) < long_window:
        return {
            "error": f"Insufficient data. Need at least {long_window} records.",
            "total_trades": 0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_return": 0.0,
            "signals": []
        }

    df = pd.DataFrame(data)
    df = df.sort_values('datetime')
    prices = df['close'].tolist()
    dates = df['datetime'].tolist()

    short_ma = calculate_moving_average(prices, short_window)
    long_ma = calculate_moving_average(prices, long_window)

    signals = generate_signals(short_ma, long_ma)

    trades = []
    position = None
    entry_price = 0

    for i in range(len(signals)):
        if signals[i] == 'BUY' and position is None:
            position = 'LONG'
            entry_price = prices[i]
            trades.append({
                'type': 'BUY',
                'date': dates[i].isoformat() if isinstance(dates[i], datetime) else dates[i],
                'price': prices[i],
                'short_ma': short_ma[i],
                'long_ma': long_ma[i]
            })
        elif signals[i] == 'SELL' and position == 'LONG':
            exit_price = prices[i]
            profit = ((exit_price - entry_price) / entry_price) * 100
            trades.append({
                'type': 'SELL',
                'date': dates[i].isoformat() if isinstance(dates[i], datetime) else dates[i],
                'price': prices[i],
                'profit_percent': round(profit, 2),
                'short_ma': short_ma[i],
                'long_ma': long_ma[i]
            })
            position = None

    completed_trades = [t for t in trades if t['type'] == 'SELL']
    profitable = len([t for t in completed_trades if t['profit_percent'] > 0])
    losing = len([t for t in completed_trades if t['profit_percent'] <= 0])
    total_return = float(sum([t['profit_percent'] for t in completed_trades]))

    win_rate = float((profitable / len(completed_trades) * 100) if len(completed_trades) > 0 else 0.0)

    return {
        "total_trades": len(completed_trades),
        "profitable_trades": profitable,
        "losing_trades": losing,
        "win_rate": round(win_rate, 2),
        "total_return": round(total_return, 2),
        "short_window": short_window,
        "long_window": long_window,
        "signals": trades[-10:]
    }
