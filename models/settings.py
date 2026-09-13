from datetime import datetime
from extensions import db


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    shop_name = db.Column(
        db.String(200),
        default="Sri Anjaneya Traders"
    )

    address = db.Column(
        db.Text,
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    email = db.Column(
        db.String(100),
        nullable=True
    )

    gst_number = db.Column(
        db.String(50),
        nullable=True
    )

    invoice_prefix = db.Column(
        db.String(20),
        default="INV"
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    @staticmethod
    def get_settings():
        settings = Settings.query.first()

        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()

        return settings