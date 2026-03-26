"""Custom exception classes for the application."""


class WealthException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, error_code: str = None):
        """Initialize exception.

        Args:
            message: Error message
            error_code: Optional error code (e.g., 'E0001')
        """
        super().__init__(message)
        self.error_code = error_code

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {super().__str__()}"
        return super().__str__()


class DataFetchException(WealthException):
    """Exception raised when data fetching fails."""

    def __init__(self, message: str = "Data fetch failed"):
        super().__init__(message, error_code="E0001")


class StorageException(WealthException):
    """Exception raised when data storage fails."""

    def __init__(self, message: str = "Storage operation failed"):
        super().__init__(message, error_code="E0003")


class PredictionException(WealthException):
    """Exception raised when prediction fails."""

    def __init__(self, message: str = "Prediction failed"):
        super().__init__(message, error_code="E0006")


class ModelException(WealthException):
    """Exception raised when model operation fails."""

    def __init__(self, message: str = "Model operation failed"):
        super().__init__(message, error_code="E0004")