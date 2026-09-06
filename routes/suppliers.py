from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.supplier import Supplier
from models.purchase import Purchase
from models.payment import Payment
from utils import login_required, log_audit, parse_float, get_search_query
from excel_export import export_suppliers

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")


@suppliers_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    query = get_search_query(Supplier, ["name", "phone"], search)
    suppliers = query.order_by(Supplier.name).all()
    return render_template("suppliers/index.html", suppliers=suppliers, search=search)


@suppliers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Supplier name is required.", "danger")
            return render_template("suppliers/form.html", supplier=None)

        opening = parse_float(request.form.get("opening_balance"))
        supplier = Supplier(
            name=name,
            phone=request.form.get("phone") or None,
            address=request.form.get("address") or None,
            opening_balance=opening,
            balance=opening,
        )
        db.session.add(supplier)
        db.session.commit()
        flash("Supplier added successfully.", "success")
        return redirect(url_for("suppliers.index"))
    return render_template("suppliers/form.html", supplier=None)


@suppliers_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    supplier = Supplier.query.get_or_404(id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Supplier name is required.", "danger")
            return render_template("suppliers/form.html", supplier=supplier)

        old_opening = supplier.opening_balance
        new_opening = parse_float(request.form.get("opening_balance"))
        diff = new_opening - old_opening

        supplier.name = name
        supplier.phone = request.form.get("phone") or None
        supplier.address = request.form.get("address") or None
        supplier.opening_balance = new_opening
        supplier.balance = supplier.balance + diff
        db.session.commit()
        flash("Supplier updated successfully.", "success")
        return redirect(url_for("suppliers.index"))
    return render_template("suppliers/form.html", supplier=supplier)


@suppliers_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    flash("Supplier deleted successfully.", "success")
    return redirect(url_for("suppliers.index"))


@suppliers_bp.route("/view/<int:id>")
@login_required
def view(id):
    supplier = Supplier.query.get_or_404(id)
    purchases = Purchase.query.filter_by(supplier_id=id).order_by(Purchase.date.desc()).all()
    payments = Payment.query.filter_by(supplier_id=id, payment_type="paid").order_by(
        Payment.date.desc()
    ).all()
    return render_template(
        "suppliers/view.html", supplier=supplier, purchases=purchases, payments=payments
    )


@suppliers_bp.route("/payment/<int:id>", methods=["GET", "POST"])
@login_required
def payment(id):
    supplier = Supplier.query.get_or_404(id)
    if request.method == "POST":
        amount = parse_float(request.form.get("amount"))
        if amount <= 0:
            flash("Payment amount must be positive.", "danger")
            return render_template("suppliers/payment.html", supplier=supplier)

        payment_obj = Payment(
            supplier_id=supplier.id,
            amount=amount,
            payment_type="paid",
            payment_mode=request.form.get("payment_mode", "Cash"),
            reference=request.form.get("reference") or None,
            date=datetime.strptime(request.form.get("date"), "%Y-%m-%d").date(),
            notes=request.form.get("notes") or None,
        )
        supplier.balance -= amount
        db.session.add(payment_obj)
        log_audit("Payment added", f"Paid ₹{amount} to {supplier.name}")
        db.session.commit()
        flash("Payment recorded successfully.", "success")
        return redirect(url_for("suppliers.view", id=id))

    return render_template("suppliers/payment.html", supplier=supplier)


@suppliers_bp.route("/export")
@login_required
def export():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return export_suppliers(suppliers)
