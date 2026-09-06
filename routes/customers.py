from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.customer import Customer
from models.bill import Bill
from models.payment import Payment
from utils import login_required, log_audit, parse_float, get_search_query
from excel_export import export_customers

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")


@customers_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    query = get_search_query(Customer, ["name", "phone"], search)
    customers = query.order_by(Customer.name).all()
    return render_template("customers/index.html", customers=customers, search=search)


@customers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Customer name is required.", "danger")
            return render_template("customers/form.html", customer=None)

        opening = parse_float(request.form.get("opening_balance"))
        customer = Customer(
            name=name,
            phone=request.form.get("phone") or None,
            address=request.form.get("address") or None,
            opening_balance=opening,
            balance=opening,
        )
        db.session.add(customer)
        db.session.commit()
        flash("Customer added successfully.", "success")
        return redirect(url_for("customers.index"))
    return render_template("customers/form.html", customer=None)


@customers_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Customer name is required.", "danger")
            return render_template("customers/form.html", customer=customer)

        old_opening = customer.opening_balance
        new_opening = parse_float(request.form.get("opening_balance"))
        diff = new_opening - old_opening

        customer.name = name
        customer.phone = request.form.get("phone") or None
        customer.address = request.form.get("address") or None
        customer.opening_balance = new_opening
        customer.balance = customer.balance + diff
        db.session.commit()
        flash("Customer updated successfully.", "success")
        return redirect(url_for("customers.index"))
    return render_template("customers/form.html", customer=customer)


@customers_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted successfully.", "success")
    return redirect(url_for("customers.index"))


@customers_bp.route("/view/<int:id>")
@login_required
def view(id):
    customer = Customer.query.get_or_404(id)
    bills = Bill.query.filter_by(customer_id=id).order_by(Bill.date.desc()).all()
    payments = Payment.query.filter_by(customer_id=id, payment_type="received").order_by(
        Payment.date.desc()
    ).all()
    return render_template(
        "customers/view.html", customer=customer, bills=bills, payments=payments
    )


@customers_bp.route("/payment/<int:id>", methods=["GET", "POST"])
@login_required
def payment(id):
    customer = Customer.query.get_or_404(id)
    if request.method == "POST":
        amount = parse_float(request.form.get("amount"))
        if amount <= 0:
            flash("Payment amount must be positive.", "danger")
            return render_template("customers/payment.html", customer=customer)

        payment_obj = Payment(
            customer_id=customer.id,
            amount=amount,
            payment_type="received",
            payment_mode=request.form.get("payment_mode", "Cash"),
            reference=request.form.get("reference") or None,
            date=datetime.strptime(request.form.get("date"), "%Y-%m-%d").date(),
            notes=request.form.get("notes") or None,
        )
        customer.balance -= amount
        db.session.add(payment_obj)
        log_audit("Payment added", f"Received ₹{amount} from {customer.name}")
        db.session.commit()
        flash("Payment recorded successfully.", "success")
        return redirect(url_for("customers.view", id=id))

    return render_template("customers/payment.html", customer=customer)


@customers_bp.route("/export")
@login_required
def export():
    customers = Customer.query.order_by(Customer.name).all()
    return export_customers(customers)
