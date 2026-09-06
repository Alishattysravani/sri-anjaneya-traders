import os
import shutil
from datetime import datetime
from flask import Blueprint, render_template, send_file, flash, redirect, url_for, current_app
from utils import login_required

backup_bp = Blueprint("backup", __name__, url_prefix="/backup")


@backup_bp.route("/")
@login_required
def index():
    db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    is_sqlite = db_uri.startswith("sqlite")
    return render_template("backup/index.html", is_sqlite=is_sqlite)


@backup_bp.route("/download")
@login_required
def download():
    db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")

    if not db_uri.startswith("sqlite"):
        flash("Direct backup download is only available for SQLite. Use PostgreSQL backup tools for production.", "warning")
        return redirect(url_for("backup.index"))

    # Extract path from sqlite:///instance/shop.db
    db_path = db_uri.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        db_path = os.path.join(current_app.root_path, db_path)

    if not os.path.exists(db_path):
        flash("Database file not found.", "danger")
        return redirect(url_for("backup.index"))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"shop_backup_{timestamp}.db"

    return send_file(
        db_path,
        as_attachment=True,
        download_name=backup_name,
        mimetype="application/octet-stream",
    )
