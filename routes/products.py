from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.product import Product
from models.category import Category
from models.brand import Brand
from models.unit import Unit
from utils import login_required, log_audit, parse_float, get_search_query
from excel_export import export_products

products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    query = get_search_query(Product, ["name", "batch_number"], search)
    products = query.order_by(Product.name).all()
    return render_template("products/index.html", products=products, search=search)


@products_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    categories = Category.query.order_by(Category.name).all()
    brands = Brand.query.order_by(Brand.name).all()
    units = Unit.query.order_by(Unit.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Product name is required.", "danger")
            return render_template("products/form.html", product=None,
                                   categories=categories, brands=brands, units=units)

        expiry = request.form.get("expiry_date") or None
        product = Product(
            name=name,
            category_id=request.form.get("category_id"),
            brand_id=request.form.get("brand_id") or None,
            unit_id=request.form.get("unit_id"),
            purchase_price=parse_float(request.form.get("purchase_price")),
            selling_price=parse_float(request.form.get("selling_price")),
            stock=max(0, parse_float(request.form.get("stock"))),
            minimum_stock=max(0, parse_float(request.form.get("minimum_stock"))),
            batch_number=request.form.get("batch_number") or None,
            expiry_date=datetime.strptime(expiry, "%Y-%m-%d").date() if expiry else None,
        )
        db.session.add(product)
        log_audit("Product added", f"Added product: {name}")
        db.session.commit()
        flash("Product added successfully.", "success")
        return redirect(url_for("products.index"))

    return render_template("products/form.html", product=None,
                           categories=categories, brands=brands, units=units)


@products_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.order_by(Category.name).all()
    brands = Brand.query.order_by(Brand.name).all()
    units = Unit.query.order_by(Unit.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Product name is required.", "danger")
            return render_template("products/form.html", product=product,
                                   categories=categories, brands=brands, units=units)

        expiry = request.form.get("expiry_date") or None
        product.name = name
        product.category_id = request.form.get("category_id")
        product.brand_id = request.form.get("brand_id") or None
        product.unit_id = request.form.get("unit_id")
        product.purchase_price = parse_float(request.form.get("purchase_price"))
        product.selling_price = parse_float(request.form.get("selling_price"))
        product.stock = max(0, parse_float(request.form.get("stock")))
        product.minimum_stock = max(0, parse_float(request.form.get("minimum_stock")))
        product.batch_number = request.form.get("batch_number") or None
        product.expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date() if expiry else None

        log_audit("Product updated", f"Updated product: {name}")
        db.session.commit()
        flash("Product updated successfully.", "success")
        return redirect(url_for("products.index"))

    return render_template("products/form.html", product=product,
                           categories=categories, brands=brands, units=units)


@products_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    product = Product.query.get_or_404(id)
    name = product.name
    db.session.delete(product)
    log_audit("Product deleted", f"Deleted product: {name}")
    db.session.commit()
    flash("Product deleted successfully.", "success")
    return redirect(url_for("products.index"))


@products_bp.route("/export")
@login_required
def export():
    products = Product.query.order_by(Product.name).all()
    return export_products(products)
