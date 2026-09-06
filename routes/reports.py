from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import func
from extensions import db
from models.bill import Bill
from models.purchase import Purchase
from models.product import Product
from models.customer import Customer
from models.supplier import Supplier
from models.payment import Payment
from utils import login_required
from excel_export import export_report

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _get_date_range(period, date_from=None, date_to=None):
    today = date.today()
    if period == "daily":
        return today, today
    elif period == "weekly":
        return today - timedelta(days=7), today
    elif period == "monthly":
        return today - timedelta(days=30), today
    elif period == "custom" and date_from and date_to:
        return date.fromisoformat(date_from), date.fromisoformat(date_to)
    return today - timedelta(days=30), today


@reports_bp.route("/")
@login_required
def index():
    return render_template("reports/index.html")


@reports_bp.route("/sales")
@login_required
def sales():
    period = request.args.get("period", "monthly")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    start, end = _get_date_range(period, date_from, date_to)

    bills = Bill.query.filter(Bill.date >= start, Bill.date <= end).order_by(Bill.date.desc()).all()
    total = sum(b.grand_total for b in bills)

    return render_template(
        "reports/sales.html", bills=bills, total=total,
        period=period, date_from=date_from or start.isoformat(),
        date_to=date_to or end.isoformat(),
    )


@reports_bp.route("/purchases")
@login_required
def purchases():
    period = request.args.get("period", "monthly")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    start, end = _get_date_range(period, date_from, date_to)

    purchases_list = Purchase.query.filter(
        Purchase.date >= start, Purchase.date <= end
    ).order_by(Purchase.date.desc()).all()
    total = sum(p.subtotal for p in purchases_list)

    return render_template(
        "reports/purchases.html", purchases=purchases_list, total=total,
        period=period, date_from=date_from or start.isoformat(),
        date_to=date_to or end.isoformat(),
    )


@reports_bp.route("/inventory")
@login_required
def inventory():
    filter_type = request.args.get("filter", "all")
    products = Product.query.order_by(Product.name).all()

    if filter_type == "low":
        products = [p for p in products if 0 < p.stock <= p.minimum_stock]
    elif filter_type == "out":
        products = [p for p in products if p.stock <= 0]
    elif filter_type == "expiring":
        products = [p for p in products if p.is_expiring_soon() or p.is_expired()]

    return render_template("reports/inventory.html", products=products, filter_type=filter_type)


@reports_bp.route("/customers")
@login_required
def customers():
    customers_list = Customer.query.order_by(Customer.name).all()
    report_data = []
    for c in customers_list:
        sales_total = db.session.query(func.coalesce(func.sum(Bill.grand_total), 0)).filter(
            Bill.customer_id == c.id
        ).scalar()
        payments_total = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.customer_id == c.id, Payment.payment_type == "received"
        ).scalar()
        report_data.append({
            "customer": c,
            "sales": sales_total,
            "payments": payments_total,
        })
    return render_template("reports/customers.html", report_data=report_data)


@reports_bp.route("/suppliers")
@login_required
def suppliers():
    suppliers_list = Supplier.query.order_by(Supplier.name).all()
    report_data = []
    for s in suppliers_list:
        purchases_total = db.session.query(func.coalesce(func.sum(Purchase.subtotal), 0)).filter(
            Purchase.supplier_id == s.id
        ).scalar()
        payments_total = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.supplier_id == s.id, Payment.payment_type == "paid"
        ).scalar()
        report_data.append({
            "supplier": s,
            "purchases": purchases_total,
            "payments": payments_total,
        })
    return render_template("reports/suppliers.html", report_data=report_data)


@reports_bp.route("/export/<report_type>")
@login_required
def export(report_type):
    period = request.args.get("period", "monthly")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    start, end = _get_date_range(period, date_from, date_to)

    if report_type == "sales":
        bills = Bill.query.filter(Bill.date >= start, Bill.date <= end).all()
        headers = ["Invoice No", "Date", "Customer", "Subtotal", "Discount", "GST", "Total", "Paid", "Balance"]
        data = [[
            b.invoice_no, b.date.strftime("%Y-%m-%d"), b.customer.name,
            b.subtotal, b.discount, b.gst, b.grand_total, b.paid_amount, b.balance,
        ] for b in bills]
        return export_report(data, headers, "Sales Report", "sales_report.xlsx")

    elif report_type == "purchases":
        purchases_list = Purchase.query.filter(Purchase.date >= start, Purchase.date <= end).all()
        headers = ["ID", "Date", "Supplier", "Subtotal", "Paid", "Balance"]
        data = [[
            p.id, p.date.strftime("%Y-%m-%d"), p.supplier.name,
            p.subtotal, p.paid_amount, p.balance,
        ] for p in purchases_list]
        return export_report(data, headers, "Purchase Report", "purchase_report.xlsx")

    elif report_type == "inventory":
        products = Product.query.all()
        headers = ["Product", "Category", "Stock", "Min Stock", "Status", "Batch", "Expiry"]
        data = [[
            p.name, p.category.name if p.category else "",
            p.stock, p.minimum_stock, p.stock_status(),
            p.batch_number or "", p.expiry_date.strftime("%Y-%m-%d") if p.expiry_date else "",
        ] for p in products]
        return export_report(data, headers, "Inventory Report", "inventory_report.xlsx")

    return redirect(url_for("reports.index"))
