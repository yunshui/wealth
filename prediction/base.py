"""Base predictor module.

Provides abstract base class for all prediction models.
"""

import os
import pickle
from abc import ABC, abstractmethod
from typing import Dict

import numpy as np

from utils.exceptions import ModelException
from utils.logger import Logger


class BasePredictor(ABC):
    """Abstract base class for all prediction models.

    This class defines the interface that all prediction models must implement.
    Subclasses must implement the abstract methods: train, predict, and
    get_feature_importance.

    Attributes:
        MODEL_VERSION: Version string for the model.
        model: The underlying model object (specific to subclass).
        _is_trained: Flag indicating if the model has been trained.
    """

    MODEL_VERSION = "1.0.0"

    def __init__(self, model_path: str = None):
        """Initialize the predictor.

        Args:
            model_path: Optional path to load a pre-trained model from.

        Raises:
            ModelException: If model_path is provided but the file doesn't exist.
        """
        self.model = None
        self._is_trained = False

        if model_path is not None:
            self.load_model(model_path)
            Logger.info(f"Loaded model from {model_path}")

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model.

        Args:
            X: Training features array of shape (n_samples, n_features).
            y: Training target array of shape (n_samples,).

        Raises:
            ModelException: If training fails.
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Features array of shape (n_samples, n_features).

        Returns:
            Predictions array of shape (n_samples,).

        Raises:
            ModelException: If model is not trained or prediction fails.
        """
        pass

    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature names to importance scores.

        Raises:
            ModelException: If model is not trained or doesn't support feature importance.
        """
        pass

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities.

        This is a default implementation that raises ModelException.
        Subclasses can override if they support probability prediction.

        Args:
            X: Features array of shape (n_samples, n_features).

        Returns:
            Probability array of shape (n_samples, n_classes).

        Raises:
            ModelException: If model is not trained or doesn't support probability prediction.
        """
        if not self.is_trained():
            raise ModelException("Model not trained")
        raise ModelException("Probability prediction not supported by this model")

    def save_model(self, path: str) -> None:
        """Save the model to a file.

        Args:
            path: Path to save the model to.

        Raises:
            ModelException: If saving fails (e.g., path doesn't exist).
        """
        if self.model is None:
            raise ModelException("No model to save")

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'is_trained': self._is_trained,
                    'version': self.MODEL_VERSION
                }, f)

            Logger.info(f"Model saved to {path}")
        except Exception as e:
            raise ModelException(f"Failed to save model: {str(e)}")

    def load_model(self, path: str) -> None:
        """Load the model from a file.

        Args:
            path: Path to load the model from.

        Raises:
            ModelException: If loading fails (e.g., file doesn't exist or is corrupted).
        """
        if not os.path.exists(path):
            raise ModelException(f"Model file not found: {path}")

        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)

            self.model = data['model']
            self._is_trained = data.get('is_trained', False)

            Logger.info(f"Model loaded from {path}, trained={self._is_trained}")
        except Exception as e:
            raise ModelException(f"Failed to load model: {str(e)}")

    def is_trained(self) -> bool:
        """Check if the model has been trained.

        Returns:
            True if the model has been trained, False otherwise.
        """
        return self._is_trained

    def get_version(self) -> str:
        """Get the model version.

        Returns:
            Version string.
        """
        return self.MODEL_VERSION