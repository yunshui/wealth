"""Logging module for the application."""

import logging
import os
from utils.config import Config

class Logger:
    """Application logger manager.

    Provides a singleton logger instance with file and console handlers.
    """

    _logger: logging.Logger = None
    _setup_complete: bool = False

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the logger singleton instance.

        Returns:
            Logger instance configured with file and console handlers
        """
        if cls._logger is None:
            cls._setup_logger()
        return cls._logger

    @classmethod
    def _setup_logger(cls) -> None:
        """Setup logger with file and console handlers."""
        if cls._setup_complete:
            return

        cls._logger = logging.getLogger('wealth')
        cls._logger.setLevel(Config.LOG_LEVEL)

        # Remove existing handlers to avoid duplicates
        cls._logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        log_file_path = os.path.join(Config.LOG_DIR, Config.LOG_FILE)
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(Config.LOG_LEVEL)
        file_handler.setFormatter(formatter)
        cls._logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(Config.LOG_LEVEL)
        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)

        cls._setup_complete = True

    @classmethod
    def info(cls, message: str) -> None:
        """Log an info message."""
        cls.get_logger().info(message)

    @classmethod
    def warning(cls, message: str) -> None:
        """Log a warning message."""
        cls.get_logger().warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        """Log an error message."""
        cls.get_logger().error(message)

    @classmethod
    def debug(cls, message: str) -> None:
        """Log a debug message."""
        cls.get_logger().debug(message)

    @classmethod
    def exception(cls, message: str) -> None:
        """Log an exception with traceback."""
        cls.get_logger().exception(message)