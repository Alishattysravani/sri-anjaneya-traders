from datetime import datetime
from extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    village = db.Column(db.String(200), nullable=True)
    address = db.Column(db.Text, nullable=True)
    opening_balance = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    bills = db.relationship("Bill", backref="customer", lazy=True)
    payments = db.relationship(
        "Payment",
        backref="customer",
        lazy=True,
        foreign_keys="Payment.customer_id",
    )
