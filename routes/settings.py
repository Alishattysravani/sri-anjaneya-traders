from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.settings import Settings
from utils import login_required

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    settings = Settings.get_settings()

    if request.method == "POST":
        settings.shop_name = request.form.get("shop_name", "").strip() or "Sri Anjaneya Traders"
        settings.address = request.form.get("address") or None
        settings.phone = request.form.get("phone") or None
        settings.email = request.form.get("email") or None
        settings.gst_number = request.form.get("gst_number") or None
        settings.invoice_prefix = request.form.get("invoice_prefix", "INV").strip() or "INV"
        db.session.commit()
        flash("Settings updated successfully.", "success")
        return redirect(url_for("settings.index"))

    return render_template("settings/index.html", settings=settings)
