"""Database initialization for app startup and CLI commands."""

import os
import logging
from flask_migrate import upgrade
from extensions import db

logger = logging.getLogger(__name__)


def _has_migration_scripts(app):
    versions_dir = os.path.join(app.root_path, "migrations", "versions")
    if not os.path.isdir(versions_dir):
        return False
    return any(
        name.endswith(".py") and name != "__init__.py"
        for name in os.listdir(versions_dir)
    )


def initialize_database(app):
    """
    Apply Alembic migrations (if present), ensure tables exist, seed defaults.
    Safe to run on every startup — seed logic is idempotent.
    """
    with app.app_context():
        if _has_migration_scripts(app):
            try:
                upgrade()
                logger.info("Database migrations applied.")
            except Exception as exc:
                logger.warning("Migration upgrade failed, falling back to create_all: %s", exc)
                db.create_all()
        else:
            db.create_all()
            logger.info("Database tables created.")

        from seeds import seed_data

        seed_data()
        logger.info("Database seed check complete.")
