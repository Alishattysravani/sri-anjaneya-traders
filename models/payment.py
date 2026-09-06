from datetime import datetime
from extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)  # received / paid
    payment_mode = db.Column(db.String(50), default="Cash")
    reference = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
