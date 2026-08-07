import logging
from app.core.config import settings

logger = logging.getLogger("app.core.config_guard")

INSECURE_JWT_SECRETS = {
    "production_super_secret_jwt_signing_key_change_in_env",
    "secret",
    "change_me",
    "default_secret"
}


def validate_production_configuration():
    """Fails fast on startup if insecure default settings are detected in production environment."""
    if settings.ENVIRONMENT == "production":
        # 1. JWT Secret Validation
        from app.core import security
        jwt_secret = getattr(security, "SECRET_KEY", settings.SECRET_KEY if hasattr(settings, "SECRET_KEY") else "")
        if jwt_secret in INSECURE_JWT_SECRETS:
            logger.critical("event=config_validation_failed reason=insecure_default_jwt_secret_in_production")
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: Default insecure JWT secret key detected in PRODUCTION mode. "
                "Must set a strong, unique SECRET_KEY environment variable."
            )

        # 2. Database URL Validation
        if "sqlite" in settings.DATABASE_URL.lower():
            logger.critical("event=config_validation_failed reason=sqlite_in_production")
            raise RuntimeError(
                "CRITICAL CONFIGURATION ERROR: SQLite database driver detected in PRODUCTION mode. "
                "Must configure PostgreSQL with AsyncPG driver for multi-tenant production stability."
            )

        logger.info("event=config_validation_success environment=%s", settings.ENVIRONMENT)
