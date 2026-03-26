"""Model trainer module - placeholder."""
import numpy as np
from utils.logger import Logger

class ModelTrainer:
    """Model trainer for all prediction models."""

    def __init__(self):
        """Initialize trainer."""
        Logger.warning("ModelTrainer is a placeholder - implement in Stage 3")

    def train_short_term(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train short-term model."""
        Logger.warning("ModelTrainer.train_short_term not implemented yet")

    def train_medium_term(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train medium-term model."""
        Logger.warning("ModelTrainer.train_medium_term not implemented yet")

    def train_long_term(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train long-term model."""
        Logger.warning("ModelTrainer.train_long_term not implemented yet")