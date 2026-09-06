from datetime import datetime, date
from extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=True)
    unit_id = db.Column(db.Integer, db.ForeignKey("units.id"), nullable=False)
    purchase_price = db.Column(db.Float, default=0.0)
    selling_price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Float, default=0.0)
    minimum_stock = db.Column(db.Float, default=0.0)
    batch_number = db.Column(db.String(100), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    purchase_items = db.relationship("PurchaseItem", backref="product", lazy=True)
    bill_items = db.relationship("BillItem", backref="product", lazy=True)
    inventory_transactions = db.relationship(
        "InventoryTransaction", backref="product", lazy=True
    )
    stock_adjustments = db.relationship("StockAdjustment", backref="product", lazy=True)

    def stock_status(self):
        if self.stock <= 0:
            return "Out of Stock"
        if self.stock <= self.minimum_stock:
            return "Low Stock"
        return "Available"

    def is_expired(self):
        if self.expiry_date and self.expiry_date < date.today():
            return True
        return False

    def is_expiring_soon(self, days=30):
        if not self.expiry_date or self.is_expired():
            return False
        delta = (self.expiry_date - date.today()).days
        return delta <= days
