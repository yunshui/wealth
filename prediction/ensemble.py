"""Ensemble prediction module integrating three time horizons."""

from typing import Dict, List
import numpy as np
import pandas as pd
from datetime import datetime

from prediction.short_term import ShortTermPredictor
from prediction.medium_term import MediumTermPredictor
from prediction.long_term import LongTermPredictor
from analysis.features import FeatureEngineer, LABEL_TO_ACTION
from data.storage import StockStorage
from utils.logger import Logger


# Default ensemble weights
DEFAULT_WEIGHTS = {
    'short': 0.3,
    'medium': 0.4,
    'long': 0.3
}


class EnsemblePredictor:
    """Ensemble predictor integrating short, medium, and long-term predictions.

    Combines predictions from three horizons using configurable weights.
    Generates a comprehensive recommendation with reasoning for each horizon.

    This class acts as a prediction service, fetching data from storage
    and returning comprehensive predictions.
    """

    def __init__(self, storage: StockStorage, weights: Dict[str, float] = None):
        """Initialize ensemble predictor.

        Args:
            storage: StockStorage instance for fetching data
            weights: Dictionary of weights for each horizon (short, medium, long)
                    Default: {'short': 0.3, 'medium': 0.4, 'long': 0.3}
        """
        self.storage = storage
        self.weights = weights or DEFAULT_WEIGHTS

        # Validate weights
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            Logger.warning(f"Ensemble weights sum to {total:.2f}, normalizing")
            self.weights = {k: v / total for k, v in self.weights.items()}

        # Initialize predictors
        self.short_predictor = ShortTermPredictor()
        self.medium_predictor = MediumTermPredictor()
        self.long_predictor = LongTermPredictor()

        Logger.info("EnsemblePredictor initialized")

    def load_models(self, model_dir: str = 'models'):
        """Load all pretrained models.

        Args:
            model_dir: Directory containing model files
        """
        import os

        try:
            self.short_predictor.load_model(os.path.join(model_dir, 'short_term.pkl'))
            Logger.info("Loaded short-term model")
        except Exception as e:
            Logger.warning(f"Failed to load short-term model: {e}")

        try:
            self.medium_predictor.load_model(os.path.join(model_dir, 'medium_term.pkl'))
            Logger.info("Loaded medium-term model")
        except Exception as e:
            Logger.warning(f"Failed to load medium-term model: {e}")

        try:
            self.long_predictor.load_model(os.path.join(model_dir, 'long_term.pkl'))
            Logger.info("Loaded long-term model")
        except Exception as e:
            Logger.warning(f"Failed to load long-term model: {e}")

    def predict(self, symbol: str) -> Dict:
        """Make prediction for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            Prediction dictionary with all horizons and ensemble
        """
        # Get stock data from storage
        df = self.storage.get_stock_data(symbol)

        if df.empty:
            Logger.warning(f"No data available for {symbol}")
            return self._empty_prediction(symbol)

        # Calculate indicators
        from analysis.indicators import IndicatorCalculator
        df = IndicatorCalculator.calculate_all(df)

        # Extract features for each horizon
        X_short = FeatureEngineer.extract_short_term_features(df, lookback=20)
        X_medium = FeatureEngineer.extract_medium_term_features(df, lookback=120)
        X_long = FeatureEngineer.extract_long_term_features(df)

        # Reshape if needed (single sample)
        if X_short.ndim == 1:
            X_short = X_short.reshape(1, -1)
        if X_medium.ndim == 1:
            X_medium = X_medium.reshape(1, -1)
        if X_long.ndim == 1:
            X_long = X_long.reshape(1, -1)

        return self._make_prediction(X_short, X_medium, X_long, symbol)

    def _empty_prediction(self, symbol: str) -> Dict:
        """Return empty prediction when no data available.

        Args:
            symbol: Stock symbol

        Returns:
            Empty prediction dictionary
        """
        return {
            'symbol': symbol,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'short': {'action': 'hold', 'confidence': 0.0, 'reasoning': ['无数据']},
            'medium': {'action': 'hold', 'confidence': 0.0, 'reasoning': ['无数据']},
            'long': {'action': 'hold', 'confidence': 0.0, 'reasoning': ['无数据']},
            'ensemble': {'action': 'hold', 'confidence': 0.0, 'breakdown': {}, 'reasoning': ['无数据']}
        }

    def _make_prediction(self, X_short: np.ndarray, X_medium: np.ndarray,
                         X_long: np.ndarray, symbol: str) -> Dict:
        """Internal method to make predictions.

        Args:
            X_short: Short-term features
            X_medium: Medium-term features
            X_long: Long-term features
            symbol: Stock symbol

        Returns:
            Prediction dictionary
        """
        result = {
            'symbol': symbol,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'short': self._predict_horizon(self.short_predictor, X_short, 'short'),
            'medium': self._predict_horizon(self.medium_predictor, X_medium, 'medium'),
            'long': self._predict_horizon(self.long_predictor, X_long, 'long')
        }

        # Generate ensemble
        result['ensemble'] = self._ensemble_predictions(result)

        return result

    def _predict_horizon(self, predictor, X: np.ndarray, horizon: str) -> Dict:
        """Make prediction for a specific horizon.

        Args:
            predictor: The predictor instance
            X: Features
            horizon: Horizon name ('short', 'medium', 'long')

        Returns:
            Prediction dictionary for this horizon
        """
        if not predictor.is_trained():
            # Return default prediction if model not trained
            return {
                'action': 'hold',
                'confidence': 0.5,
                'reasoning': ['模型未训练，使用默认预测']
            }

        predictions, confidence = predictor.predict_with_confidence(X)

        prediction = int(predictions[0])
        confidence = float(confidence[0])

        # Generate reasoning
        reasoning = predictor.generate_reasoning(X, prediction, confidence)

        return {
            'action': LABEL_TO_ACTION.get(prediction, 'hold'),
            'confidence': confidence,
            'reasoning': reasoning
        }

    def _ensemble_predictions(self, predictions: Dict) -> Dict:
        """Ensemble predictions from all horizons.

        Args:
            predictions: Dictionary with predictions for each horizon

        Returns:
            Ensemble prediction
        """
        # Calculate weighted scores for each action
        action_scores = {'buy': 0.0, 'sell': 0.0, 'hold': 0.0}

        # Get predictions
        short_pred = predictions['short']
        medium_pred = predictions['medium']
        long_pred = predictions['long']

        # Weight by horizon
        action_scores[short_pred['action']] += short_pred['confidence'] * self.weights['short']
        action_scores[medium_pred['action']] += medium_pred['confidence'] * self.weights['medium']
        action_scores[long_pred['action']] += long_pred['confidence'] * self.weights['long']

        # Select action with highest score
        ensemble_action = max(action_scores, key=action_scores.get)
        ensemble_confidence = action_scores[ensemble_action]

        # Generate reasoning
        reasoning = []
        if short_pred['action'] == ensemble_action:
            reasoning.append(f"短期建议{short_pred['action']}")
        if medium_pred['action'] == ensemble_action:
            reasoning.append(f"中期建议{medium_pred['action']}")
        if long_pred['action'] == ensemble_action:
            reasoning.append(f"长期建议{long_pred['action']}")

        # Combine all reasoning
        all_reasoning = []
        all_reasoning.extend(short_pred['reasoning'])
        all_reasoning.extend(medium_pred['reasoning'])
        all_reasoning.extend(long_pred['reasoning'])

        return {
            'action': ensemble_action,
            'confidence': ensemble_confidence,
            'breakdown': action_scores,
            'reasoning': reasoning,
            'all_reasoning': all_reasoning
        }

    def batch_predict(self, symbols: List[str]) -> Dict[str, Dict]:
        """Make predictions for multiple stocks.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to predictions
        """
        results = {}

        for symbol in symbols:
            try:
                # Make prediction using self.storage
                prediction = self.predict(symbol)
                results[symbol] = prediction

            except Exception as e:
                Logger.error(f"Failed to predict {symbol}: {str(e)}")

        return results
