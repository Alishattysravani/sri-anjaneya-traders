"""Default seed data — idempotent, safe to run on every startup."""

from werkzeug.security import generate_password_hash
from extensions import db
from models.user import User
from models.category import Category
from models.unit import Unit
from models.settings import Settings


def seed_data():
    """Create default admin, categories, units, and settings if missing."""
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password_hash=generate_password_hash("admin123"),
        )
        db.session.add(admin)

    for name in ["Fertilizer", "Seeds", "Pesticides"]:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))

    for name in ["Bag", "KG", "Litre", "Packet"]:
        if not Unit.query.filter_by(name=name).first():
            db.session.add(Unit(name=name))

    Settings.get_settings()
    db.session.commit()
