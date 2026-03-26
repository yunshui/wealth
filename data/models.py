"""Data models for the stock prediction system."""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Stock:
    """Stock basic information."""

    symbol: str
    name: str
    industry: Optional[str] = None
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    list_date: Optional[str] = None

@dataclass
class StockData:
    """Stock historical data with technical indicators."""

    date: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    # Technical indicators
    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    kdj_k: Optional[float] = None
    kdj_d: Optional[float] = None
    kdj_j: Optional[float] = None
    rsi6: Optional[float] = None
    rsi12: Optional[float] = None
    rsi24: Optional[float] = None
    boll_upper: Optional[float] = None
    boll_middle: Optional[float] = None
    boll_lower: Optional[float] = None
    obv: Optional[float] = None

@dataclass
class Prediction:
    """Prediction result for a stock."""

    date: str
    symbol: str
    horizon: str  # 'short', 'medium', 'long'
    action: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0-1
    reasoning: List[str]
    model_version: str

@dataclass
class Sector:
    """Sector information."""

    sector_id: str
    sector_name: str
    sector_type: str  # 'industry' or 'concept'
    leader_count: int = 0

@dataclass
class SectorLeader:
    """Sector leading stock."""

    sector_id: str
    sector_name: str
    symbol: str
    score: float
    rank: int
    market_cap_rank: int
    volume_rank: int