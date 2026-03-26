"""Tests for helper functions module."""

import pytest
from datetime import datetime
from utils.helpers import (
    format_date, format_price, format_volume,
    calculate_return, action_to_chinese, color_for_action
)

def test_format_date():
    """Test date formatting"""
    dt = datetime(2024, 1, 15)
    assert format_date(dt) == '2024-01-15'
    assert format_date('2024-01-15') == '2024-01-15'

def test_format_price():
    """Test price formatting"""
    assert format_price(12.3456) == '12.35'
    assert format_price(100) == '100.00'

def test_format_volume():
    """Test volume formatting"""
    assert format_volume(1000) == '1000'
    assert format_volume(10000) == '1.00万'
    assert format_volume(100000000) == '1.00亿'

def test_calculate_return():
    """Test return calculation"""
    assert calculate_return(100, 110) == 0.1
    assert calculate_return(110, 100) == -0.09090909090909091

def test_action_to_chinese():
    """Test action to Chinese conversion"""
    assert action_to_chinese('buy') == '买入'
    assert action_to_chinese('sell') == '卖出'
    assert action_to_chinese('hold') == '持有'
    assert action_to_chinese('unknown') == 'unknown'

def test_color_for_action():
    """Test color mapping for actions"""
    assert color_for_action('buy') == 'red'
    assert color_for_action('sell') == 'green'
    assert color_for_action('hold') == 'gray'
    assert color_for_action('unknown') == 'gray'