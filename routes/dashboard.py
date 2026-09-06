from datetime import date, timedelta
from flask import Blueprint, render_template
from sqlalchemy import func
from extensions import db
from models.product import Product
from models.customer import Customer
from models.supplier import Supplier
from models.bill import Bill
from models.purchase import Purchase
from utils import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    today = date.today()

    total_products = Product.query.count()
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    total_stock = db.session.query(func.coalesce(func.sum(Product.stock), 0)).scalar()

    todays_sales = (
        db.session.query(func.coalesce(func.sum(Bill.grand_total), 0))
        .filter(Bill.date == today)
        .scalar()
    )
    todays_purchases = (
        db.session.query(func.coalesce(func.sum(Purchase.subtotal), 0))
        .filter(Purchase.date == today)
        .scalar()
    )
    customer_outstanding = (
        db.session.query(func.coalesce(func.sum(Customer.balance), 0)).scalar()
    )
    supplier_outstanding = (
        db.session.query(func.coalesce(func.sum(Supplier.balance), 0)).scalar()
    )

    low_stock_products = Product.query.filter(
        Product.stock <= Product.minimum_stock
    ).order_by(Product.stock.asc()).limit(10).all()

    recent_sales = Bill.query.order_by(Bill.created_at.desc()).limit(5).all()
    recent_purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(5).all()

    expiring_soon = Product.query.filter(
        Product.expiry_date.isnot(None),
        Product.expiry_date <= today + timedelta(days=30),
        Product.expiry_date >= today,
    ).limit(5).all()

    expired_products = Product.query.filter(
        Product.expiry_date.isnot(None),
        Product.expiry_date < today,
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_customers=total_customers,
        total_suppliers=total_suppliers,
        todays_sales=todays_sales,
        todays_purchases=todays_purchases,
        total_stock=total_stock,
        customer_outstanding=customer_outstanding,
        supplier_outstanding=supplier_outstanding,
        low_stock_products=low_stock_products,
        recent_sales=recent_sales,
        recent_purchases=recent_purchases,
        expiring_soon=expiring_soon,
        expired_products=expired_products,
    )
