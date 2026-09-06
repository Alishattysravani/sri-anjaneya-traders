from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.category import Category
from utils import login_required, log_audit

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.route("/")
@login_required
def index():
    categories = Category.query.order_by(Category.name).all()
    return render_template("categories/index.html", categories=categories)


@categories_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Category name is required.", "danger")
            return render_template("categories/form.html", category=None)
        if Category.query.filter_by(name=name).first():
            flash("Category already exists.", "danger")
            return render_template("categories/form.html", category=None)
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash("Category added successfully.", "success")
        return redirect(url_for("categories.index"))
    return render_template("categories/form.html", category=None)


@categories_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Category name is required.", "danger")
            return render_template("categories/form.html", category=category)
        category.name = name
        db.session.commit()
        flash("Category updated successfully.", "success")
        return redirect(url_for("categories.index"))
    return render_template("categories/form.html", category=category)


@categories_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    category = Category.query.get_or_404(id)
    if category.products:
        flash("Cannot delete category with linked products.", "danger")
        return redirect(url_for("categories.index"))
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted successfully.", "success")
    return redirect(url_for("categories.index"))
