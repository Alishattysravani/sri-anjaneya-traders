from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import db
from models.purchase import Purchase, PurchaseItem
from models.supplier import Supplier
from models.product import Product
from utils import login_required, log_audit, parse_float, record_inventory_transaction, get_search_query
from excel_export import export_purchases

purchases_bp = Blueprint("purchases", __name__, url_prefix="/purchases")


@purchases_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    query = Purchase.query.join(Supplier)
    if search:
        from sqlalchemy import or_, cast, String
        query = query.filter(
            or_(
                Supplier.name.ilike(f"%{search}%"),
                Purchase.invoice_number.ilike(f"%{search}%"),
                cast(Purchase.id, String).ilike(f"%{search}%"),
            )
        )
    purchases = query.order_by(Purchase.date.desc()).all()
    return render_template("purchases/index.html", purchases=purchases, search=search)


@purchases_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    products = Product.query.order_by(Product.name).all()

    if request.method == "POST":
        supplier_id = request.form.get("supplier_id")
        if not supplier_id:
            flash("Please select a supplier.", "danger")
            return render_template("purchases/form.html", suppliers=suppliers, products=products)

        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        prices = request.form.getlist("price[]")

        if not product_ids:
            flash("Add at least one product.", "danger")
            return render_template("purchases/form.html", suppliers=suppliers, products=products)

        try:
            supplier = Supplier.query.get_or_404(int(supplier_id))
            purchase_date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
            paid_amount = parse_float(request.form.get("paid_amount"))
            invoice_number = request.form.get("invoice_number") or None

            subtotal = 0.0
            items_data = []

            for pid, qty, price in zip(product_ids, quantities, prices):
                quantity = parse_float(qty)
                unit_price = parse_float(price)
                if quantity <= 0 or unit_price < 0:
                    raise ValueError("Invalid quantity or price.")
                total = quantity * unit_price
                subtotal += total
                items_data.append((int(pid), quantity, unit_price, total))

            balance = subtotal - paid_amount

            purchase = Purchase(
                supplier_id=supplier.id,
                invoice_number=invoice_number,
                date=purchase_date,
                subtotal=subtotal,
                paid_amount=paid_amount,
                balance=balance,
            )
            db.session.add(purchase)
            db.session.flush()

            for pid, quantity, unit_price, total in items_data:
                product = Product.query.get(pid)
                if not product:
                    raise ValueError("Product not found.")

                item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=pid,
                    quantity=quantity,
                    price=unit_price,
                    total=total,
                )
                db.session.add(item)

                record_inventory_transaction(
                    product, "in", quantity,
                    reference_type="purchase", reference_id=purchase.id,
                    notes=f"Purchase #{purchase.id}",
                )
                product.purchase_price = unit_price

            supplier.balance += balance
            log_audit("Purchase created", f"Purchase #{purchase.id} from {supplier.name}")
            db.session.commit()
            flash("Purchase recorded successfully.", "success")
            return redirect(url_for("purchases.index"))

        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception:
            db.session.rollback()
            flash("Error saving purchase. Please try again.", "danger")

    return render_template("purchases/form.html", suppliers=suppliers, products=products)


@purchases_bp.route("/view/<int:id>")
@login_required
def view(id):
    purchase = Purchase.query.get_or_404(id)
    return render_template("purchases/view.html", purchase=purchase)


@purchases_bp.route("/export")
@login_required
def export():
    purchases = Purchase.query.order_by(Purchase.date.desc()).all()
    return export_purchases(purchases)
