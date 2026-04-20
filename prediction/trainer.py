"""Model trainer for training all prediction models."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os

from prediction.short_term import ShortTermPredictor
from prediction.medium_term import MediumTermPredictor
from prediction.long_term import LongTermPredictor
from analysis.features import FeatureEngineer
from analysis.indicators import IndicatorCalculator
from data.storage import StockStorage
from utils.logger import Logger


class ModelTrainer:
    """Model trainer for training all prediction models.

    Handles data preparation, training, and evaluation
    for short, medium, and long-term predictors.
    """

    def __init__(self, storage: StockStorage, model_dir: str = 'models'):
        """Initialize model trainer.

        Args:
            storage: StockStorage instance for fetching data
            model_dir: Directory to save trained models
        """
        self.storage = storage
        self.model_dir = model_dir

        # Initialize predictors
        self.short_predictor = ShortTermPredictor()
        self.medium_predictor = MediumTermPredictor()
        self.long_predictor = LongTermPredictor()

        Logger.info("ModelTrainer initialized")

    def prepare_training_data(self, horizon: str, symbols: List[str] = None,
                             lookback: int = None, label_horizon: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for a specific horizon.

        Args:
            horizon: Prediction horizon ('short', 'medium', 'long')
            symbols: List of stock symbols to use (None for all stocks)
            lookback: Number of days to look back for features
            label_horizon: Number of days ahead for labels

        Returns:
            Tuple of (features, labels)
        """
        # Default parameters
        if horizon == 'short':
            lookback = lookback or 20
            label_horizon = label_horizon or 5
        elif horizon == 'medium':
            lookback = lookback or 120
            label_horizon = label_horizon or 60
        else:  # long
            lookback = lookback or 252
            label_horizon = label_horizon or 120

        Logger.info(f"Preparing training data for {horizon} horizon (lookback={lookback}, label_horizon={label_horizon})")

        # Get stock list
        if symbols is None:
            stocks = self.storage.get_stock_list()
        else:
            stocks = [{'symbol': s} for s in symbols]

        if not stocks:
            Logger.warning("No stocks found for training")
            return np.array([]), np.array([])

        X_list = []
        y_list = []

        for stock in stocks:
            symbol = stock['symbol']
            try:
                # Get stock data
                df = self.storage.get_stock_data(symbol)

                data_count = len(df)
                min_required = lookback + label_horizon

                if df.empty or data_count < min_required:
                    Logger.debug(f"{symbol}: Insufficient data (have {data_count}, need {min_required})")
                    continue

                # Calculate indicators
                df = IndicatorCalculator.calculate_all(df)

                # Create labels for all data points
                labels = FeatureEngineer.create_labels(df, label_horizon)

                # Extract features for each valid time point
                # Start from lookback point, end before label_horizon from the end
                start_idx = lookback
                end_idx = len(df) - label_horizon

                samples_count = 0
                first_feature_count = None

                for i in range(start_idx, end_idx):
                    # Get lookback window
                    window_df = df.iloc[i - lookback:i].copy()

                    # Skip if window is too small (in case of gaps)
                    if len(window_df) < lookback:
                        continue

                    # Extract features for this time point
                    try:
                        if horizon == 'short':
                            features = FeatureEngineer.extract_short_term_features(window_df, lookback)
                        elif horizon == 'medium':
                            features = FeatureEngineer.extract_medium_term_features(window_df, lookback)
                        else:
                            features = FeatureEngineer.extract_long_term_features(window_df)

                        # Track feature count for consistency check
                        if first_feature_count is None:
                            first_feature_count = len(features)
                        elif len(features) != first_feature_count:
                            Logger.warning(f"{symbol}: Feature count mismatch! Expected {first_feature_count}, got {len(features)} at index {i}")

                        # Check if features are valid
                        if len(features) == 1 and features[0] == 0:
                            # Invalid features (insufficient data)
                            continue

                        # Get label for this time point
                        label = labels[i]

                        # Use all samples (not excluding HOLD)
                        # This is important for balanced training
                        X_list.append(features)
                        y_list.append(label)
                        samples_count += 1

                    except Exception as e:
                        Logger.debug(f"{symbol}: Failed to extract features at index {i}: {str(e)}")
                        continue

                if samples_count > 0:
                    Logger.debug(f"{symbol}: Extracted {samples_count} training samples (feature_dim={first_feature_count})")
                else:
                    Logger.warning(f"{symbol}: No valid samples extracted from {data_count} data points")

            except Exception as e:
                Logger.warning(f"Failed to prepare data for {symbol}: {str(e)}")
                continue

        if not X_list:
            Logger.warning("No valid training samples found")
            return np.array([]), np.array([])

        # Validate all feature vectors have the same dimension
        feature_dims = [len(x) for x in X_list]
        unique_dims = set(feature_dims)

        if len(unique_dims) > 1:
            Logger.error(f"Feature dimension mismatch! Found {len(unique_dims)} different dimensions: {sorted(unique_dims)}")
            Logger.error("This will cause np.vstack to fail. Please check feature extraction logic.")
            # Log samples of each dimension for debugging
            for dim in sorted(unique_dims):
                count = feature_dims.count(dim)
                Logger.error(f"  - {count} samples with dimension {dim}")
            return np.array([]), np.array([])

        # Combine all samples
        X = np.vstack(X_list)
        y = np.array(y_list)

        Logger.info(f"Prepared {len(X)} training samples for {horizon} horizon (feature_dim={X.shape[1]})")
        Logger.info(f"Label distribution: Hold={np.sum(y==0)}, Buy={np.sum(y==1)}, Sell={np.sum(y==2)}")

        return X, y

    def train_short_term_model(self, symbols: List[str] = None) -> Dict[str, float]:
        """Train short-term model.

        Args:
            symbols: List of stock symbols to use (None for all stocks)

        Returns:
            Training metrics
        """
        Logger.info("Training short-term model")

        # Prepare data
        X, y = self.prepare_training_data('short', symbols)

        if len(X) == 0:
            Logger.error("No training data available")
            return {'error': 'No training data available'}

        # Train model
        metrics = self.short_predictor.train(X, y, test_size=0.2)

        # Save model
        model_path = os.path.join(self.model_dir, 'short_term.pkl')
        self.short_predictor.save_model(model_path)

        return metrics

    def train_medium_term_model(self, symbols: List[str] = None) -> Dict[str, float]:
        """Train medium-term model.

        Args:
            symbols: List of stock symbols to use (None for all stocks)

        Returns:
            Training metrics
        """
        Logger.info("Training medium-term model")

        # Prepare data
        X, y = self.prepare_training_data('medium', symbols)

        if len(X) == 0:
            Logger.error("No training data available")
            return {'error': 'No training data available'}

        # Train model
        metrics = self.medium_predictor.train(X, y, test_size=0.2)

        # Save model
        model_path = os.path.join(self.model_dir, 'medium_term.pkl')
        self.medium_predictor.save_model(model_path)

        return metrics

    def train_long_term_model(self, symbols: List[str] = None) -> Dict[str, float]:
        """Train long-term model.

        Args:
            symbols: List of stock symbols to use (None for all stocks)

        Returns:
            Training metrics
        """
        Logger.info("Training long-term model")

        # Prepare data
        X, y = self.prepare_training_data('long', symbols)

        if len(X) == 0:
            Logger.error("No training data available")
            return {'error': 'No training data available'}

        # Train model
        metrics = self.long_predictor.train(X, y, test_size=0.2)

        # Save model
        model_path = os.path.join(self.model_dir, 'long_term.pkl')
        self.long_predictor.save_model(model_path)

        return metrics

    def train_all_models(self, symbols: List[str] = None) -> Dict[str, Dict[str, float]]:
        """Train all models.

        Args:
            symbols: List of stock symbols to use (None for all stocks)

        Returns:
            Dictionary of metrics for each model
        """
        Logger.info("Training all models")

        # Create model directory
        os.makedirs(self.model_dir, exist_ok=True)

        results = {
            'short': self.train_short_term_model(symbols),
            'medium': self.train_medium_term_model(symbols),
            'long': self.train_long_term_model(symbols)
        }

        Logger.info("All models trained successfully")
        return results

    def evaluate_model(self, predictor, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate a model.

        Args:
            predictor: The predictor to evaluate
            X_test: Test features
            y_test: Test labels

        Returns:
            Evaluation metrics
        """
        y_pred = predictor.predict(X_test)

        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }

    def load_models(self) -> bool:
        """Load all trained models.

        Returns:
            True if all models loaded successfully
        """
        try:
            self.short_predictor.load_model(os.path.join(self.model_dir, 'short_term.pkl'))
            self.medium_predictor.load_model(os.path.join(self.model_dir, 'medium_term.pkl'))
            self.long_predictor.load_model(os.path.join(self.model_dir, 'long_term.pkl'))
            Logger.info("All models loaded successfully")
            return True
        except Exception as e:
            Logger.error(f"Failed to load models: {str(e)}")
            return False
