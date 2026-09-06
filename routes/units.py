from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.unit import Unit
from utils import login_required

units_bp = Blueprint("units", __name__, url_prefix="/units")


@units_bp.route("/")
@login_required
def index():
    units = Unit.query.order_by(Unit.name).all()
    return render_template("units/index.html", units=units)


@units_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Unit name is required.", "danger")
            return render_template("units/form.html", unit=None)
        if Unit.query.filter_by(name=name).first():
            flash("Unit already exists.", "danger")
            return render_template("units/form.html", unit=None)
        unit = Unit(name=name)
        db.session.add(unit)
        db.session.commit()
        flash("Unit added successfully.", "success")
        return redirect(url_for("units.index"))
    return render_template("units/form.html", unit=None)


@units_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    unit = Unit.query.get_or_404(id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Unit name is required.", "danger")
            return render_template("units/form.html", unit=unit)
        unit.name = name
        db.session.commit()
        flash("Unit updated successfully.", "success")
        return redirect(url_for("units.index"))
    return render_template("units/form.html", unit=unit)


@units_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    unit = Unit.query.get_or_404(id)
    if unit.products:
        flash("Cannot delete unit with linked products.", "danger")
        return redirect(url_for("units.index"))
    db.session.delete(unit)
    db.session.commit()
    flash("Unit deleted successfully.", "success")
    return redirect(url_for("units.index"))
