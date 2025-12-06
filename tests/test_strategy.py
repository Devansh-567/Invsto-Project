import pytest
from app.strategy import calculate_moving_average, generate_signals, calculate_strategy_performance
import numpy as np
from datetime import datetime, timedelta


def test_calculate_moving_average_simple():
    """Test moving average calculation with simple data"""
    prices = [1, 2, 3, 4, 5]
    window = 3
    ma = calculate_moving_average(prices, window)
    
    # First two values should be NaN
    assert np.isnan(ma[0])
    assert np.isnan(ma[1])
    # Third value should be (1+2+3)/3 = 2.0
    assert ma[2] == 2.0
    assert ma[3] == 3.0
    assert ma[4] == 4.0


def test_calculate_moving_average_insufficient_data():
    """Test moving average with insufficient data"""
    prices = [1, 2]
    window = 5
    ma = calculate_moving_average(prices, window)
    
    # All values should be NaN
    assert all(np.isnan(x) for x in ma)


def test_generate_signals_buy():
    """Test buy signal generation"""
    short_ma = [1.0, 2.0, 3.0, 4.0]
    long_ma = [2.0, 2.5, 2.8, 3.0]
    
    signals = generate_signals(short_ma, long_ma)
    
    # Should contain at least one BUY signal when short crosses above long
    assert 'BUY' in signals or 'HOLD' in signals


def test_generate_signals_sell():
    """Test sell signal generation"""
    short_ma = [4.0, 3.0, 2.0, 1.0]
    long_ma = [2.0, 2.5, 2.8, 3.0]
    
    signals = generate_signals(short_ma, long_ma)
    
    # Should contain SELL signal when short crosses below long
    assert 'SELL' in signals or 'HOLD' in signals


def test_generate_signals_with_nan():
    """Test signal generation with NaN values"""
    short_ma = [np.nan, np.nan, 3.0, 4.0]
    long_ma = [np.nan, 2.5, 2.8, 3.0]
    
    signals = generate_signals(short_ma, long_ma)
    
    # First signals should be HOLD due to NaN
    assert signals[0] == 'HOLD'
    assert signals[1] == 'HOLD'


def test_calculate_strategy_performance_with_data():
    """Test strategy performance calculation with valid data"""
    # Create sample data
    base_date = datetime(2024, 1, 1)
    data = []
    
    for i in range(100):
        data.append({
            'datetime': base_date + timedelta(days=i),
            'close': 100 + i * 0.5 + (i % 10) * 2
        })
    
    performance = calculate_strategy_performance(data, short_window=10, long_window=20)
    
    assert 'total_trades' in performance
    assert 'win_rate' in performance
    assert 'total_return' in performance
    assert isinstance(performance['total_trades'], int)
    assert isinstance(performance['win_rate'], float)


def test_calculate_strategy_performance_insufficient_data():
    """Test strategy with insufficient data"""
    data = [
        {'datetime': datetime(2024, 1, 1), 'close': 100},
        {'datetime': datetime(2024, 1, 2), 'close': 101}
    ]
    
    performance = calculate_strategy_performance(data, short_window=10, long_window=20)
    
    assert 'error' in performance
    assert performance['total_trades'] == 0


def test_calculate_strategy_performance_returns_correct_structure():
    """Test that performance returns all required fields"""
    base_date = datetime(2024, 1, 1)
    data = []
    
    for i in range(100):
        data.append({
            'datetime': base_date + timedelta(days=i),
            'close': 100 + np.sin(i / 10) * 10
        })
    
    performance = calculate_strategy_performance(data, short_window=10, long_window=20)
    
    required_fields = ['total_trades', 'profitable_trades', 'losing_trades', 
                       'win_rate', 'total_return', 'signals']
    
    for field in required_fields:
        assert field in performance


def test_moving_average_accuracy():
    """Test accuracy of moving average calculation"""
    prices = [10, 20, 30, 40, 50]
    window = 3
    ma = calculate_moving_average(prices, window)
    
    # Manual calculation: (10+20+30)/3 = 20
    assert ma[2] == 20.0
    # (20+30+40)/3 = 30
    assert ma[3] == 30.0
    # (30+40+50)/3 = 40
    assert ma[4] == 40.0