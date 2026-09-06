from datetime import datetime
from extensions import db


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    opening_balance = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    purchases = db.relationship("Purchase", backref="supplier", lazy=True)
    payments = db.relationship(
        "Payment",
        backref="supplier",
        lazy=True,
        foreign_keys="Payment.supplier_id",
    )
