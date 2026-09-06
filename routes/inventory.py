from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.product import Product
from models.inventory import StockAdjustment, InventoryTransaction
from utils import login_required, log_audit, parse_float, record_inventory_transaction

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    products = query.order_by(Product.name).all()

    today = date.today()
    expiring_soon = [p for p in products if p.is_expiring_soon()]
    expired = [p for p in products if p.is_expired()]

    return render_template(
        "inventory/index.html",
        products=products,
        search=search,
        expiring_soon=expiring_soon,
        expired=expired,
    )


@inventory_bp.route("/adjust", methods=["GET", "POST"])
@login_required
def adjust():
    products = Product.query.order_by(Product.name).all()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        adjustment_type = request.form.get("adjustment_type")
        quantity = parse_float(request.form.get("quantity"))
        reason = request.form.get("reason") or None
        adj_date = request.form.get("date")

        if not product_id or quantity <= 0:
            flash("Valid product and quantity are required.", "danger")
            return render_template("inventory/adjust.html", products=products)

        try:
            product = Product.query.get_or_404(int(product_id))
            previous_stock = product.stock

            if adjustment_type == "increase":
                new_stock = previous_stock + quantity
                txn_type = "in"
                adj_qty = quantity
            elif adjustment_type == "decrease":
                if previous_stock < quantity:
                    raise ValueError("Cannot decrease below zero stock.")
                new_stock = previous_stock - quantity
                txn_type = "out"
                adj_qty = quantity
            else:
                raise ValueError("Invalid adjustment type.")

            adjustment = StockAdjustment(
                product_id=product.id,
                quantity=quantity,
                adjustment_type=adjustment_type,
                reason=reason,
                date=date.fromisoformat(adj_date) if adj_date else date.today(),
            )
            db.session.add(adjustment)
            db.session.flush()

            record_inventory_transaction(
                product, txn_type, adj_qty,
                reference_type="adjustment", reference_id=adjustment.id,
                notes=reason,
            )

            log_audit("Stock adjusted", f"{adjustment_type} {quantity} for {product.name}")
            db.session.commit()
            flash("Stock adjusted successfully.", "success")
            return redirect(url_for("inventory.index"))

        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception:
            db.session.rollback()
            flash("Error adjusting stock.", "danger")

    return render_template("inventory/adjust.html", products=products)


@inventory_bp.route("/transactions")
@login_required
def transactions():
    txns = InventoryTransaction.query.order_by(InventoryTransaction.date.desc()).limit(100).all()
    return render_template("inventory/transactions.html", transactions=txns)
