from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.brand import Brand
from utils import login_required

brands_bp = Blueprint("brands", __name__, url_prefix="/brands")


@brands_bp.route("/")
@login_required
def index():
    brands = Brand.query.order_by(Brand.name).all()
    return render_template("brands/index.html", brands=brands)


@brands_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Brand name is required.", "danger")
            return render_template("brands/form.html", brand=None)
        if Brand.query.filter_by(name=name).first():
            flash("Brand already exists.", "danger")
            return render_template("brands/form.html", brand=None)
        brand = Brand(name=name)
        db.session.add(brand)
        db.session.commit()
        flash("Brand added successfully.", "success")
        return redirect(url_for("brands.index"))
    return render_template("brands/form.html", brand=None)


@brands_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Brand name is required.", "danger")
            return render_template("brands/form.html", brand=brand)
        brand.name = name
        db.session.commit()
        flash("Brand updated successfully.", "success")
        return redirect(url_for("brands.index"))
    return render_template("brands/form.html", brand=brand)


@brands_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    brand = Brand.query.get_or_404(id)
    if brand.products:
        flash("Cannot delete brand with linked products.", "danger")
        return redirect(url_for("brands.index"))
    db.session.delete(brand)
    db.session.commit()
    flash("Brand deleted successfully.", "success")
    return redirect(url_for("brands.index"))
