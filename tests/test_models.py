"""Tests for data models."""

import pytest
from data.models import Stock, StockData, Prediction, Sector, SectorLeader


def test_stock_creation():
    """Test Stock dataclass creation"""
    stock = Stock(
        symbol='000001.SZ',
        name='平安银行',
        industry='银行',
        sector='金融',
        market_cap=2345.6
    )
    assert stock.symbol == '000001.SZ'
    assert stock.name == '平安银行'
    assert stock.market_cap == 2345.6


def test_stock_data_creation():
    """Test StockData dataclass creation"""
    data = StockData(
        date='2024-01-15',
        symbol='000001.SZ',
        open=12.0,
        high=12.5,
        low=11.8,
        close=12.3,
        volume=1000000,
        ma5=12.1,
        ma10=11.9
    )
    assert data.date == '2024-01-15'
    assert data.close == 12.3
    assert data.ma5 == 12.1


def test_prediction_creation():
    """Test Prediction dataclass creation"""
    pred = Prediction(
        date='2024-01-15',
        symbol='000001.SZ',
        horizon='short',
        action='buy',
        confidence=0.78,
        reasoning=['MACD金叉', '量价配合'],
        model_version='1.0'
    )
    assert pred.horizon == 'short'
    assert pred.action == 'buy'
    assert pred.confidence == 0.78
    assert len(pred.reasoning) == 2


def test_sector_creation():
    """Test Sector dataclass creation"""
    sector = Sector(
        sector_id='industry_001',
        sector_name='银行',
        sector_type='industry'
    )
    assert sector.sector_type == 'industry'


def test_sector_leader_creation():
    """Test SectorLeader dataclass creation"""
    leader = SectorLeader(
        sector_id='industry_001',
        sector_name='银行',
        symbol='000001.SZ',
        score=0.85,
        rank=1,
        market_cap_rank=1,
        volume_rank=3
    )
    assert leader.rank == 1
    assert leader.market_cap_rank == 1