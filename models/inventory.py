from datetime import datetime
from extensions import db


class InventoryTransaction(db.Model):
    __tablename__ = "inventory_transactions"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # in / out / adjust
    quantity = db.Column(db.Float, nullable=False)
    previous_stock = db.Column(db.Float, nullable=False)
    new_stock = db.Column(db.Float, nullable=False)
    reference_type = db.Column(db.String(50), nullable=True)  # purchase, bill, adjustment
    reference_id = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)


class StockAdjustment(db.Model):
    __tablename__ = "stock_adjustments"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    adjustment_type = db.Column(db.String(20), nullable=False)  # increase / decrease
    reason = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
