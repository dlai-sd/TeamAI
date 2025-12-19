"""
Logging configuration for the application
Structured logging with JSON format for production
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
import json

class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON logs"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: str = None
):
    """
    Configure application logging
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        log_format: Format type ('json' or 'text')
        log_file: Optional file path for logs
    """
    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        if log_format == "json":
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
        
        logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)


# Request logging decorator
def log_request(func):
    """Decorator to log API requests"""
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(
            f"API Request: {func.__name__}",
            extra={"function": func.__name__, "args": str(kwargs)}
        )
        
        try:
            result = await func(*args, **kwargs)
            logger.info(
                f"API Success: {func.__name__}",
                extra={"function": func.__name__}
            )
            return result
        except Exception as e:
            logger.error(
                f"API Error: {func.__name__} - {str(e)}",
                extra={"function": func.__name__, "error": str(e)},
                exc_info=True
            )
            raise
    
    return wrapper
