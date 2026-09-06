from datetime import datetime
from extensions import db


class Bill(db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    subtotal = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    gst = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    payment_mode = db.Column(db.String(50), default="Cash")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "BillItem", backref="bill", lazy=True, cascade="all, delete-orphan"
    )


class BillItem(db.Model):
    __tablename__ = "bill_items"

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
