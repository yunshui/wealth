"""Tests for custom exception classes."""

import pytest
from utils.exceptions import (
    WealthException,
    DataFetchException,
    StorageException,
    PredictionException,
    ModelException
)


def test_wealth_exception():
    """Test base exception can be created."""
    exc = WealthException("Test error")
    assert str(exc) == "Test error"
    assert isinstance(exc, Exception)


def test_data_fetch_exception():
    """Test DataFetchException inherits from WealthException."""
    exc = DataFetchException("Fetch failed")
    assert isinstance(exc, WealthException)
    assert isinstance(exc, Exception)


def test_storage_exception():
    """Test StorageException inherits from WealthException."""
    exc = StorageException("Storage failed")
    assert isinstance(exc, WealthException)


def test_prediction_exception():
    """Test PredictionException inherits from WealthException."""
    exc = PredictionException("Prediction failed")
    assert isinstance(exc, WealthException)


def test_model_exception():
    """Test ModelException inherits from WealthException."""
    exc = ModelException("Model failed")
    assert isinstance(exc, WealthException)


def test_wealth_exception_with_error_code():
    """Test WealthException with error_code."""
    exc = WealthException("Test error", error_code="E9999")
    assert str(exc) == "[E9999] Test error"


def test_data_fetch_exception_error_code():
    """Test DataFetchException has correct error code."""
    exc = DataFetchException("Network timeout")
    assert str(exc) == "[E0001] Network timeout"


def test_storage_exception_error_code():
    """Test StorageException has correct error code."""
    exc = StorageException("Database locked")
    assert str(exc) == "[E0003] Database locked"


def test_prediction_exception_error_code():
    """Test PredictionException has correct error code."""
    exc = PredictionException("Invalid input")
    assert str(exc) == "[E0006] Invalid input"


def test_model_exception_error_code():
    """Test ModelException has correct error code."""
    exc = ModelException("Model not found")
    assert str(exc) == "[E0004] Model not found"


def test_data_fetch_exception_default_message():
    """Test DataFetchException default message."""
    exc = DataFetchException()
    assert str(exc) == "[E0001] Data fetch failed"


def test_storage_exception_default_message():
    """Test StorageException default message."""
    exc = StorageException()
    assert str(exc) == "[E0003] Storage operation failed"


def test_prediction_exception_default_message():
    """Test PredictionException default message."""
    exc = PredictionException()
    assert str(exc) == "[E0006] Prediction failed"


def test_model_exception_default_message():
    """Test ModelException default message."""
    exc = ModelException()
    assert str(exc) == "[E0004] Model operation failed"