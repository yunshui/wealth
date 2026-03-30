"""Sector analysis module for identifying leading stocks."""

from typing import List, Tuple
from utils.logger import Logger
from data.storage import StockStorage
from analysis.indicators import IndicatorCalculator
import pandas as pd


class SectorAnalyzer:
    """Sector analyzer for identifying leading stocks in each sector."""

    def __init__(self, storage: StockStorage):
        """Initialize sector analyzer.

        Args:
            storage: StockStorage instance
        """
        self.storage = storage
        Logger.info("SectorAnalyzer initialized")

    def identify_leaders(self, sector_id: str, sector_name: str, limit: int = 20) -> List[dict]:
        """Identify leading stocks in a sector.

        Args:
            sector_id: Sector ID
            sector_name: Sector name
            limit: Maximum number of leaders to return

        Returns:
            List of leader dictionaries with symbol, score, rank, etc.
        """
        Logger.info(f"Identifying leaders for sector: {sector_name}")

        # Get stocks in the sector
        stocks = self.storage.get_stock_list(sector=sector_name)

        if not stocks:
            Logger.warning(f"No stocks found for sector: {sector_name}")
            return []

        # Batch calculate scores for all stocks
        symbols = [stock['symbol'] for stock in stocks]
        stock_scores = self._batch_calculate_scores(stocks, symbols)

        # Sort by score
        stock_scores.sort(key=lambda x: x['score'], reverse=True)

        # Batch calculate ranks for efficiency
        top_symbols = [s['symbol'] for s in stock_scores[:limit]]
        market_cap_ranks = self.rank_by_market_cap(top_symbols)
        volume_ranks = self.rank_by_volume(top_symbols)

        rank_dict = {symbol: rank for rank, symbol in enumerate(market_cap_ranks, 1)}
        volume_dict = {symbol: rank for rank, (symbol, _) in enumerate(volume_ranks, 1)}

        # Create leaders list with rankings
        leaders = []
        for i, item in enumerate(stock_scores[:limit], 1):
            leaders.append({
                'sector_id': sector_id,
                'sector_name': sector_name,
                'symbol': item['symbol'],
                'score': item['score'],
                'rank': i,
                'market_cap_rank': rank_dict.get(item['symbol'], 0),
                'volume_rank': volume_dict.get(item['symbol'], 0)
            })

        Logger.info(f"Identified {len(leaders)} leaders for sector: {sector_name}")
        return leaders

    def _batch_calculate_scores(self, stocks: List[dict], symbols: List[str]) -> List[dict]:
        """Batch calculate scores for multiple stocks with optimized queries.

        Args:
            stocks: List of stock dictionaries
            symbols: List of stock symbols

        Returns:
            List of dictionaries with symbol and score
        """
        stock_scores = []
        for stock in stocks:
            try:
                symbol = stock['symbol']
                score = self.calculate_sector_score(symbol)
                stock_scores.append({
                    'symbol': symbol,
                    'score': score,
                    'market_cap': stock.get('market_cap', 0)
                })
            except Exception as e:
                Logger.warning(f"Failed to calculate score for {stock['symbol']}: {str(e)}")
                continue

        return stock_scores

    def calculate_sector_score(self, symbol: str, cached_data: dict = None) -> float:
        """Calculate comprehensive score for a stock in its sector.

        Args:
            symbol: Stock symbol
            cached_data: Optional pre-fetched data dict {symbol: (stock_info, df)}

        Returns:
            Score between 0 and 1
        """
        try:
            # Use cached data if available (for batch operations)
            if cached_data and symbol in cached_data:
                stock, df = cached_data[symbol]
            else:
                # Get stock info
                stock = self.storage.get_stock(symbol)
                if not stock:
                    return 0.0

                # Get recent stock data
                df = self.storage.get_stock_data(symbol, end_date=None)
                if df.empty or len(df) < 20:
                    return 0.0

            df = df.tail(60)  # Use last 60 days
            df = IndicatorCalculator.calculate_all(df)

            # Calculate component scores
            market_cap_score = self._calculate_market_cap_score(stock.get('market_cap', 0))
            volume_score = self._calculate_volume_score(df)
            trend_score = self._calculate_trend_score(df)
            stability_score = self._calculate_stability_score(df)

            # Weighted average
            score = (
                market_cap_score * 0.35 +
                volume_score * 0.25 +
                trend_score * 0.25 +
                stability_score * 0.15
            )

            return min(max(score, 0.0), 1.0)  # Normalize to 0-1

        except Exception as e:
            Logger.error(f"Failed to calculate sector score for {symbol}: {str(e)}")
            return 0.0

    def _calculate_market_cap_score(self, market_cap: float) -> float:
        """Calculate market cap score (normalized to 0-1)."""
        # Larger market cap gets higher score, capped at 10000亿
        return min(market_cap / 10000.0, 1.0)

    def _calculate_volume_score(self, df: pd.DataFrame) -> float:
        """Calculate volume score based on recent activity."""
        if 'volume' not in df.columns or len(df) < 5:
            return 0.0

        # Compare recent average volume to historical average
        recent_avg = df['volume'].tail(5).mean()
        historical_avg = df['volume'].mean()

        if historical_avg == 0:
            return 0.5

        # Recent higher volume = higher score, cap at 2x
        ratio = recent_avg / historical_avg
        return min(ratio / 2.0, 1.0)

    def _calculate_trend_score(self, df: pd.DataFrame) -> float:
        """Calculate trend score based on price movement."""
        if 'close' not in df.columns or len(df) < 20:
            return 0.5

        # Calculate returns over different periods
        returns_5 = (df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6] if len(df) > 5 else 0
        returns_20 = (df['close'].iloc[-1] - df['close'].iloc[-21]) / df['close'].iloc[-21] if len(df) > 20 else 0

        # Positive trend gets higher score
        # 5% 5-day return or 10% 20-day return = 1.0
        score = (max(returns_5, 0) * 10 + max(returns_20, 0) * 5) / 2
        return min(score, 1.0)

    def _calculate_stability_score(self, df: pd.DataFrame) -> float:
        """Calculate stability score based on price volatility."""
        if 'close' not in df.columns or len(df) < 10:
            return 0.5

        # Calculate volatility (standard deviation of returns)
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()

        # Lower volatility = higher stability score
        # 5% daily volatility = 0.5 score
        score = max(0, 1.0 - volatility / 0.1)
        return score

    def rank_by_market_cap(self, symbols: List[str]) -> List[str]:
        """Rank stocks by market cap.

        Args:
            symbols: List of stock symbols

        Returns:
            List of symbols ranked by market cap (descending)
        """
        stock_mcap = []
        for symbol in symbols:
            stock = self.storage.get_stock(symbol)
            if stock and stock.get('market_cap'):
                stock_mcap.append((symbol, stock['market_cap']))

        # Sort by market cap descending
        stock_mcap.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in stock_mcap]

    def rank_by_volume(self, symbols: List[str], days: int = 20) -> List[Tuple[str, float]]:
        """Rank stocks by average volume.

        Args:
            symbols: List of stock symbols
            days: Number of recent days to average

        Returns:
            List of (symbol, avg_volume) tuples ranked by volume (descending)
        """
        volumes = []
        for symbol in symbols:
            try:
                df = self.storage.get_stock_data(symbol)
                if not df.empty and 'volume' in df.columns:
                    recent_df = df.tail(days)
                    avg_volume = recent_df['volume'].mean()
                    volumes.append((symbol, avg_volume))
            except Exception as e:
                Logger.warning(f"Failed to get volume for {symbol}: {str(e)}")

        # Sort by volume descending
        volumes.sort(key=lambda x: x[1], reverse=True)
        return volumes

    def update_all_sector_leaders(self):
        """Update leaders for all sectors."""
        Logger.info("Updating all sector leaders...")

        # Get all sectors
        sectors = self.storage.get_all_sectors()

        total_updated = 0
        for sector in sectors:
            try:
                leaders = self.identify_leaders(
                    sector['sector_id'],
                    sector['sector_name']
                )

                if leaders:
                    self.storage.save_sector_leaders(sector['sector_id'], leaders)
                    total_updated += 1

            except Exception as e:
                Logger.error(f"Failed to update leaders for {sector['sector_name']}: {str(e)}")

        Logger.info(f"Updated leaders for {total_updated}/{len(sectors)} sectors")