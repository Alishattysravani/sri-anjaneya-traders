"""Shared utility functions for the application."""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from extensions import db
from models.audit import AuditLog
from models.settings import Settings
from models.bill import Bill
from models.inventory import InventoryTransaction


PAYMENT_MODES = ["Cash", "UPI", "Credit"]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def log_audit(action, description=None):
    """Record an audit log entry for the current user."""
    user_id = session.get("user_id")
    entry = AuditLog(user_id=user_id, action=action, description=description)
    db.session.add(entry)


def generate_invoice_number():
    """Generate unique invoice number using configured prefix."""
    settings = Settings.get_settings()
    prefix = settings.invoice_prefix or "INV"
    last_bill = Bill.query.order_by(Bill.id.desc()).first()
    if last_bill:
        try:
            last_num = int(last_bill.invoice_no.split("-")[-1])
        except (ValueError, IndexError):
            last_num = last_bill.id
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}-{new_num:04d}"


def record_inventory_transaction(
    product, transaction_type, quantity, reference_type=None, reference_id=None, notes=None
):
    """Create inventory transaction and update product stock."""
    previous_stock = product.stock
    if transaction_type == "in":
        new_stock = previous_stock + quantity
    elif transaction_type == "out":
        new_stock = previous_stock - quantity
    else:
        new_stock = quantity  # for adjust, quantity is the new stock value

    if new_stock < 0:
        raise ValueError("Stock cannot be negative.")

    product.stock = new_stock
    txn = InventoryTransaction(
        product_id=product.id,
        transaction_type=transaction_type,
        quantity=abs(quantity) if transaction_type != "adjust" else quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes,
    )
    db.session.add(txn)
    return txn


def parse_float(value, default=0.0):
    try:
        return float(value) if value not in (None, "") else default
    except (ValueError, TypeError):
        return default


def get_search_query(model, search_fields, search_term):
    """Build OR filter for search across multiple fields."""
    if not search_term:
        return model.query
    from sqlalchemy import or_

    filters = []
    for field_name in search_fields:
        field = getattr(model, field_name)
        filters.append(field.ilike(f"%{search_term}%"))
    return model.query.filter(or_(*filters))
