from datetime import datetime
from flask import Blueprint, render_template, request
from sqlalchemy import or_

from extensions import db
from models.bill import Bill
from models.customer import Customer
from models.settings import Settings
from utils import login_required
from excel_export import export_bills


bills_bp = Blueprint("bills", __name__, url_prefix="/bills")


@bills_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")

    query = Bill.query.join(Customer)

    if search:
        query = query.filter(
            or_(
                Bill.invoice_no.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
            )
        )

    if date_from:
        query = query.filter(
            Bill.date >= datetime.strptime(date_from, "%Y-%m-%d").date()
        )

    if date_to:
        query = query.filter(
            Bill.date <= datetime.strptime(date_to, "%Y-%m-%d").date()
        )

    bills = query.order_by(Bill.date.desc()).all()

    return render_template(
        "bills/index.html",
        bills=bills,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


@bills_bp.route("/view/<int:id>")
@login_required
def view(id):
    bill = Bill.query.get_or_404(id)

    return render_template(
        "bills/view.html",
        bill=bill
    )


@bills_bp.route("/invoice/<int:id>")
@login_required
def invoice(id):
    bill = Bill.query.get_or_404(id)
    settings = Settings.get_settings()

    # Get category from the first product in the bill
    category_name = ""

    if bill.items:
        first_item = bill.items[0]

        if first_item.product and first_item.product.category:
            category_name = first_item.product.category.name.lower().strip()

    # Select invoice template based on product category
    if "fertilizer" in category_name or "fertiliser" in category_name:
        template = "bills/invoice1.html"

    elif "pesticide" in category_name:
        template = "bills/invoice2.html"

    elif "seed" in category_name:
        template = "bills/invoice3.html"

    else:
        # Default template
        template = "bills/invoice1.html"

    return render_template(
        template,
        bill=bill,
        settings=settings
    )


@bills_bp.route("/export")
@login_required
def export():
    bills = Bill.query.order_by(Bill.date.desc()).all()

    return export_bills(bills)