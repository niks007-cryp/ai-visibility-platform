import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configures application-wide structured logging handlers and formatters."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
    )

    # Configure specific third-party logger levels
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )

    logger = logging.getLogger("app")
    logger.info(
        f"Logging initialized. Level: {settings.LOG_LEVEL}, Env: {settings.ENVIRONMENT}"
    )
