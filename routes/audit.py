from flask import Blueprint, render_template
from models.audit import AuditLog
from utils import login_required

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")


@audit_bp.route("/")
@login_required
def index():
    logs = AuditLog.query.order_by(AuditLog.date.desc()).limit(200).all()
    return render_template("audit/index.html", logs=logs)
