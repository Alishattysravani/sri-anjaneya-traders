from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import db
from models.bill import Bill, BillItem
from models.customer import Customer
from models.product import Product
from utils import (
    login_required, log_audit, parse_float, generate_invoice_number,
    record_inventory_transaction, PAYMENT_MODES,
)

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")


@sales_bp.route("/")
@login_required
def index():
    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.filter(Product.stock > 0).order_by(Product.name).all()
    return render_template("sales/form.html", customers=customers, products=products,
                           payment_modes=PAYMENT_MODES)


@sales_bp.route("/create", methods=["POST"])
@login_required
def create():
    customer_id = request.form.get("customer_id")
    if not customer_id:
        flash("Please select a customer.", "danger")
        return redirect(url_for("sales.index"))

    product_ids = request.form.getlist("product_id[]")
    quantities = request.form.getlist("quantity[]")
    prices = request.form.getlist("price[]")

    if not product_ids:
        flash("Add at least one product.", "danger")
        return redirect(url_for("sales.index"))

    try:
        customer = Customer.query.get_or_404(int(customer_id))
        bill_date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
        discount = parse_float(request.form.get("discount"))
        gst = parse_float(request.form.get("gst"))
        paid_amount = parse_float(request.form.get("paid_amount"))
        payment_mode = request.form.get("payment_mode", "Cash")

        subtotal = 0.0
        items_data = []

        for pid, qty, price in zip(product_ids, quantities, prices):
            quantity = parse_float(qty)
            unit_price = parse_float(price)
            if quantity <= 0 or unit_price < 0:
                raise ValueError("Invalid quantity or price.")

            product = Product.query.get(int(pid))
            if not product:
                raise ValueError("Product not found.")
            if product.stock < quantity:
                raise ValueError(f"Insufficient stock for {product.name}. Available: {product.stock}")

            total = quantity * unit_price
            subtotal += total
            items_data.append((product, quantity, unit_price, total))

        grand_total = subtotal - discount + gst
        if grand_total < 0:
            grand_total = 0
        balance = grand_total - paid_amount

        invoice_no = generate_invoice_number()
        bill = Bill(
            invoice_no=invoice_no,
            customer_id=customer.id,
            date=bill_date,
            subtotal=subtotal,
            discount=discount,
            gst=gst,
            grand_total=grand_total,
            paid_amount=paid_amount,
            balance=balance,
            payment_mode=payment_mode,
        )
        db.session.add(bill)
        db.session.flush()

        for product, quantity, unit_price, total in items_data:
            item = BillItem(
                bill_id=bill.id,
                product_id=product.id,
                quantity=quantity,
                price=unit_price,
                total=total,
            )
            db.session.add(item)
            record_inventory_transaction(
                product, "out", quantity,
                reference_type="bill", reference_id=bill.id,
                notes=f"Bill {invoice_no}",
            )

        customer.balance += balance
        log_audit("Bill created", f"Bill {invoice_no} for {customer.name}")
        db.session.commit()
        flash(f"Bill {invoice_no} created successfully.", "success")
        return redirect(url_for("bills.invoice", id=bill.id))

    except ValueError as e:
        db.session.rollback()
        flash(str(e), "danger")
    except Exception:
        db.session.rollback()
        flash("Error creating bill. Please try again.", "danger")

    return redirect(url_for("sales.index"))


@sales_bp.route("/product/<int:id>")
@login_required
def product_info(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        "id": product.id,
        "name": product.name,
        "selling_price": product.selling_price,
        "stock": product.stock,
        "unit": product.unit.name if product.unit else "",
    })
