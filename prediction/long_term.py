"""Long-term prediction model (3+ months)."""

from typing import Dict, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from prediction.base import BasePredictor
from analysis.features import FeatureEngineer, LABEL_TO_ACTION
from utils.logger import Logger


class LongTermPredictor(BasePredictor):
    """Long-term predictor for 3+ month predictions.

    Uses long-term trends, value indicators, and fundamentals
    to predict long-term price movements.

    Default model: RandomForestClassifier with deeper trees
    """

    def __init__(self, model_type: str = 'random_forest', model_path: str = None):
        """Initialize long-term predictor.

        Args:
            model_type: Type of model ('random_forest' or 'logistic')
            model_path: Optional path to load model from
        """
        super().__init__(model_path)
        self.model_type = model_type
        self.horizon = 'long'
        if not model_path:
            self._init_model()

    def _init_model(self):
        """Initialize the underlying model."""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=10,
                min_samples_leaf=4,
                random_state=42,
                n_jobs=-1
            )
            Logger.info("Initialized Random Forest model for long-term prediction")
        elif self.model_type == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            )
            Logger.info("Initialized Logistic Regression model for long-term prediction")
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict[str, float]:
        """Train the model.

        Args:
            X: Feature matrix
            y: Target labels (0=hold, 1=buy, 2=sell)
            test_size: Proportion of data for testing

        Returns:
            Training metrics dictionary
        """
        Logger.info(f"Training long-term model with {len(X)} samples")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_normalized, y, test_size=test_size, random_state=42, stratify=y
        )

        # Train model
        self.model.fit(X_train, y_train)
        self._is_trained = True

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        Logger.info(f"Long-term model trained. Test accuracy: {accuracy:.3f}")

        return {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Feature matrix

        Returns:
            Predicted labels (0=hold, 1=buy, 2=sell)
        """
        if not self.is_trained():
            raise ValueError("Model not trained. Call train() first.")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        return self.model.predict(X_normalized)

    def predict_with_confidence(self, X: np.ndarray) -> tuple:
        """Make predictions with confidence scores.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (predictions, confidence)
        """
        if not self.is_trained():
            raise ValueError("Model not trained. Call train() first.")

        # Normalize features
        X_normalized = FeatureEngineer.normalize_features(X)

        predictions = self.model.predict(X_normalized)
        proba = self.model.predict_proba(X_normalized)

        confidence = np.max(proba, axis=1)

        return predictions, confidence

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature indices to importance scores
        """
        if not self.is_trained():
            return {}

        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            return {f'feature_{i}': float(imp) for i, imp in enumerate(importances)}
        else:
            Logger.warning("Model does not support feature importance")
            return {}

    def generate_reasoning(self, features: np.ndarray, prediction: int, confidence: float) -> List[str]:
        """Generate human-readable reasoning for prediction.

        Args:
            features: Feature vector
            prediction: Predicted label (0=hold, 1=buy, 2=sell)
            confidence: Confidence score

        Returns:
            List of reasoning strings
        """
        reasoning = []

        action = LABEL_TO_ACTION.get(prediction, 'hold')
        reasoning.append(f"长期预测({confidence:.1%}置信度): {action}")

        return reasoning
