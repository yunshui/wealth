"""Short-term predictor module - placeholder."""
from prediction.base import BasePredictor

class ShortTermPredictor(BasePredictor):
    """Short-term prediction model (1-5 days)."""

    def __init__(self):
        super().__init__("ShortTermPredictor")