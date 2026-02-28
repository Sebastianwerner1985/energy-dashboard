"""
Logging utility for Energy Dashboard
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name: str, level: str = None) -> logging.Logger:
    """
    Set up a logger with console and file handlers

    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Get log level from environment or use INFO as default
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO').upper()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'energy_dashboard.log'),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")

    return logger


def log_exception(logger: logging.Logger, exception: Exception, context: str = None):
    """
    Log an exception with context

    Args:
        logger: Logger instance
        exception: Exception to log
        context: Additional context information
    """
    if context:
        logger.error(f"{context}: {type(exception).__name__}: {str(exception)}")
    else:
        logger.error(f"{type(exception).__name__}: {str(exception)}")

    logger.debug("Exception details:", exc_info=True)
