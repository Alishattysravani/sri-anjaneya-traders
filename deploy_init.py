"""Manual database initialization (optional CLI helper)."""

from wsgi import app
from db_init import initialize_database


def main():
    initialize_database(app)
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
