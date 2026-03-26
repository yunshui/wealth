import pytest
import numpy as np
from prediction.base import BasePredictor
from utils.exceptions import ModelException

def test_base_predictor_is_abstract():
    """Test that BasePredictor cannot be instantiated directly"""
    with pytest.raises(TypeError):
        BasePredictor()

def test_base_predictor_methods_are_abstract():
    """Test that abstract methods are defined"""
    class TestPredictor(BasePredictor):
        def __init__(self):
            super().__init__(model_path=None)
            self.model = None

        def train(self, X, y):
            pass

        def predict(self, X):
            return np.array([1])

        def get_feature_importance(self):
            return {}

    predictor = TestPredictor()
    assert predictor.is_trained() == False
    assert predictor.get_version() == "1.0.0"
from prediction.short_term import ShortTermPredictor
from prediction.medium_term import MediumTermPredictor
from prediction.long_term import LongTermPredictor

def test_short_term_predictor_initialization():
    """Test ShortTermPredictor initialization"""
    predictor = ShortTermPredictor()
    assert predictor.model_type == 'random_forest'
    assert predictor.horizon == 'short'

def test_short_term_predictor_train_and_predict():
    """Test ShortTermPredictor training and prediction"""
    predictor = ShortTermPredictor()

    # Create dummy data
    X = np.random.rand(100, 20)
    y = np.random.randint(0, 3, 100)

    predictor.train(X, y)

    # Make predictions
    X_test = np.random.rand(10, 20)
    predictions = predictor.predict(X_test)

    assert len(predictions) == 10
    assert all(p in [0, 1, 2] for p in predictions)

def test_short_term_predictor_feature_importance():
    """Test getting feature importance"""
    predictor = ShortTermPredictor()

    X = np.random.rand(100, 20)
    y = np.random.randint(0, 3, 100)

    predictor.train(X, y)

    importance = predictor.get_feature_importance()
    assert importance is not None
    assert len(importance) > 0

def test_medium_term_predictor_initialization():
    """Test MediumTermPredictor initialization"""
    predictor = MediumTermPredictor()
    assert predictor.model_type == 'random_forest'
    assert predictor.horizon == 'medium'

def test_medium_term_predictor_train_and_predict():
    """Test MediumTermPredictor training and prediction"""
    predictor = MediumTermPredictor()

    X = np.random.rand(100, 25)
    y = np.random.randint(0, 3, 100)

    predictor.train(X, y)

    X_test = np.random.rand(10, 25)
    predictions = predictor.predict(X_test)

    assert len(predictions) == 10
    assert all(p in [0, 1, 2] for p in predictions)

def test_long_term_predictor_initialization():
    """Test LongTermPredictor initialization"""
    predictor = LongTermPredictor()
    assert predictor.model_type == 'random_forest'
    assert predictor.horizon == 'long'

def test_long_term_predictor_train_and_predict():
    """Test LongTermPredictor training and prediction"""
    predictor = LongTermPredictor()

    X = np.random.rand(100, 30)
    y = np.random.randint(0, 3, 100)

    predictor.train(X, y)

    X_test = np.random.rand(10, 30)
    predictions = predictor.predict(X_test)

    assert len(predictions) == 10
    assert all(p in [0, 1, 2] for p in predictions)
