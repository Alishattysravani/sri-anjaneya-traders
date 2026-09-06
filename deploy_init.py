"""Initialize database on first deploy (Render/production)."""

from app import app, seed_data
from extensions import db


def main():
    with app.app_context():
        db.create_all()
        seed_data()
        print("Database initialized successfully.")


if __name__ == "__main__":
    main()
