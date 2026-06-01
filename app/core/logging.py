import logging
import sys
from loguru import logger
from app.core.config import settings

def setup_logging():
    # Remove default handlers
    logger.remove()

    # Console handler with rich formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )

    # File handler (optional - for production)
    logger.add(
        "logs/media_service_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="30 days",
        level="INFO",
        enqueue=True,
    )

    # Intercept standard logging (for SQLAlchemy, etc.)
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    logger.info("Logging system initialized")
    return logger


# Global logger instance
log = setup_logging()