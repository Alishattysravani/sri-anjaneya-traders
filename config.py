import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    _database_url = os.environ.get("DATABASE_URL")
    if _database_url:
        SQLALCHEMY_DATABASE_URI = _database_url
        if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
                "postgres://", "postgresql://", 1
            )
    else:
        # Default SQLite path (set at app init if needed)
        SQLALCHEMY_DATABASE_URI = "sqlite:///shop.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
