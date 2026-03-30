"""Error handling utilities for the application."""

from typing import Callable, Optional, Any
from functools import wraps
from utils.logger import Logger
from utils.exceptions import (
    DatabaseException,
    StorageException,
    DataFetchException,
    ModelException,
    PredictionException
)


def handle_errors(
    default_return: Any = None,
    log_error: bool = True,
    show_user_message: bool = True,
    user_message: str = "操作失败，请稍后重试"
):
    """Decorator for handling errors consistently across the application.

    Args:
        default_return: Value to return if an error occurs
        log_error: Whether to log the error
        show_user_message: Whether to show a user-friendly message
        user_message: Default user-friendly message

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (DatabaseException, StorageException, DataFetchException,
                   ModelException, PredictionException) as e:
                if log_error:
                    Logger.error(f"Error in {func.__name__}: {str(e)}")
                if show_user_message:
                    Logger.info(f"User message: {user_message}")
                return default_return
            except Exception as e:
                if log_error:
                    Logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                if show_user_message:
                    Logger.info(f"User message: {user_message}")
                return default_return
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """Safely execute a function with error handling.

    Args:
        func: Function to execute
        args: Positional arguments for the function
        default: Default value to return on error
        kwargs: Keyword arguments for the function

    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        Logger.error(f"Error executing {func.__name__}: {str(e)}")
        return default


def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, Optional[str]]:
    """Validate that all required fields are present in data.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "数据为空"

    missing_fields = [field for field in required_fields if field not in data or data[field] is None]

    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"

    return True, None


def get_user_friendly_error(error: Exception) -> str:
    """Get a user-friendly error message.

    Args:
        error: Exception object

    Returns:
        User-friendly error message
    """
    error_type = type(error).__name__

    error_messages = {
        'DatabaseException': '数据库错误，请检查数据库连接',
        'StorageException': '数据存储错误，请稍后重试',
        'DataFetchException': '数据获取失败，请检查网络连接',
        'ModelException': '模型错误，请检查模型文件',
        'PredictionException': '预测失败，请检查输入数据',
        'FileNotFoundError': '文件不存在',
        'ConnectionError': '网络连接失败',
        'TimeoutError': '操作超时，请稍后重试',
        'ValueError': '输入值无效',
        'KeyError': '缺少必要的数据字段',
    }

    return error_messages.get(error_type, f"发生错误: {error_type}")


class ErrorHandler:
    """Central error handler for the application."""

    @staticmethod
    def handle_database_error(error: Exception, operation: str = "数据库操作") -> str:
        """Handle database errors.

        Args:
            error: Exception object
            operation: Description of the operation

        Returns:
            User-friendly error message
        """
        Logger.error(f"Database error during {operation}: {str(error)}")
        return f"数据库操作失败: {operation}"

    @staticmethod
    def handle_data_fetch_error(error: Exception, symbol: str = None) -> str:
        """Handle data fetch errors.

        Args:
            error: Exception object
            symbol: Stock symbol being fetched

        Returns:
            User-friendly error message
        """
        context = f"获取股票 {symbol} 数据" if symbol else "获取数据"
        Logger.error(f"Data fetch error: {str(error)}")
        return f"{context}失败，请检查网络连接"

    @staticmethod
    def handle_model_error(error: Exception, model_name: str = None) -> str:
        """Handle model errors.

        Args:
            error: Exception object
            model_name: Name of the model

        Returns:
            User-friendly error message
        """
        context = f"加载模型 {model_name}" if model_name else "模型操作"
        Logger.error(f"Model error: {str(error)}")
        return f"{context}失败，请检查模型文件"

    @staticmethod
    def handle_prediction_error(error: Exception, symbol: str = None) -> str:
        """Handle prediction errors.

        Args:
            error: Exception object
            symbol: Stock symbol being predicted

        Returns:
            User-friendly error message
        """
        context = f"股票 {symbol}" if symbol else "股票"
        Logger.error(f"Prediction error: {str(error)}")
        return f"{context}预测失败，请检查数据是否完整"