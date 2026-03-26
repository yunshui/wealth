import pytest
import pandas as pd
import numpy as np
from analysis.indicators import IndicatorCalculator

def test_calculate_ma():
    """Test MA calculation"""
    df = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    })
    result = IndicatorCalculator.calculate_ma(df, [5, 10])

    assert 'ma5' in result.columns
    assert 'ma10' in result.columns
    assert abs(result.loc[4, 'ma5'] - 12.0) < 0.01

def test_calculate_macd():
    """Test MACD calculation"""
    df = pd.DataFrame({
        'close': [10 + i * 0.5 for i in range(30)]
    })
    result = IndicatorCalculator.calculate_macd(df)

    assert 'macd' in result.columns
    assert 'macd_signal' in result.columns
    assert 'macd_hist' in result.columns

def test_calculate_kdj():
    """Test KDJ calculation"""
    df = pd.DataFrame({
        'high': [10 + i for i in range(20)],
        'low': [10 + i - 2 for i in range(20)],
        'close': [10 + i - 1 for i in range(20)]
    })
    result = IndicatorCalculator.calculate_kdj(df)

    assert 'kdj_k' in result.columns
    assert 'kdj_d' in result.columns
    assert 'kdj_j' in result.columns

def test_calculate_rsi():
    """Test RSI calculation"""
    df = pd.DataFrame({
        'close': [10 + i * 0.5 for i in range(30)]
    })
    result = IndicatorCalculator.calculate_rsi(df, [6, 12])

    assert 'rsi6' in result.columns
    assert 'rsi12' in result.columns

def test_calculate_boll():
    """Test BOLL calculation"""
    df = pd.DataFrame({
        'close': [10 + i * 0.2 for i in range(30)]
    })
    result = IndicatorCalculator.calculate_boll(df)

    assert 'boll_upper' in result.columns
    assert 'boll_middle' in result.columns
    assert 'boll_lower' in result.columns

def test_calculate_obv():
    """Test OBV calculation"""
    df = pd.DataFrame({
        'close': [10, 11, 10, 11, 12],
        'volume': [1000, 1500, 1200, 1300, 1400]
    })
    result = IndicatorCalculator.calculate_obv(df)

    assert 'obv' in result

def test_calculate_all():
    """Test calculate all indicators"""
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'open': [10 + i * 0.1 for i in range(100)],
        'high': [10.5 + i * 0.1 for i in range(100)],
        'low': [9.5 + i * 0.1 for i in range(100)],
        'close': [10 + i * 0.1 for i in range(100)],
        'volume': [10000 + i * 100 for i in range(100)]
    })
    result = IndicatorCalculator.calculate_all(df)

    expected_columns = ['ma5', 'ma10', 'ma20', 'ma60', 'macd', 'macd_signal', 'macd_hist',
                       'kdj_k', 'kdj_d', 'kdj_j', 'rsi6', 'rsi12', 'rsi24',
                       'boll_upper', 'boll_middle', 'boll_lower', 'obv']

    for col in expected_columns:
        assert col in result.columns