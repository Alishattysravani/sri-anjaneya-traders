import os
import click
from werkzeug.security import generate_password_hash
from flask import Flask
from config import Config
from extensions import db, migrate
import models  # noqa: F401 - register models
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.products import products_bp
from routes.categories import categories_bp
from routes.brands import brands_bp
from routes.units import units_bp
from routes.customers import customers_bp
from routes.suppliers import suppliers_bp
from routes.purchases import purchases_bp
from routes.sales import sales_bp
from routes.bills import bills_bp
from routes.inventory import inventory_bp
from routes.reports import reports_bp
from routes.settings import settings_bp
from routes.audit import audit_bp
from routes.backup import backup_bp


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    # Normalize SQLite paths to absolute instance folder path
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///"):
        db_file = db_uri.replace("sqlite:///", "")
        if not os.path.isabs(db_file):
            if db_file.startswith("instance/") or db_file.startswith("instance\\"):
                db_file = os.path.join(app.root_path, db_file)
            else:
                db_file = os.path.join(app.instance_path, os.path.basename(db_file))
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
            db_file = db_file.replace("\\", "/")
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
    elif not os.environ.get("DATABASE_URL"):
        db_path = os.path.join(app.instance_path, "shop.db").replace("\\", "/")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(units_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(backup_bp)

    @app.cli.command("init-db")
    def init_db():
        """Initialize database and seed default data."""
        db.create_all()
        seed_data()
        click.echo("Database initialized with default data.")

    @app.cli.command("seed")
    def seed():
        """Seed default data."""
        seed_data()
        click.echo("Seed data created.")

    return app


def seed_data():
    from models.user import User
    from models.category import Category
    from models.unit import Unit
    from models.settings import Settings

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password_hash=generate_password_hash("admin123"),
        )
        db.session.add(admin)
        print("Created admin user (username: admin, password: admin123)")

    for name in ["Fertilizer", "Seeds", "Pesticides"]:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))

    for name in ["Bag", "KG", "Litre", "Packet"]:
        if not Unit.query.filter_by(name=name).first():
            db.session.add(Unit(name=name))

    Settings.get_settings()
    db.session.commit()


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host="0.0.0.0", port=5000)
